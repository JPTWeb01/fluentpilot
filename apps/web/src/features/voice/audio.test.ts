import { describe, expect, it } from "vitest";

import { base64ToBlob, blobToBase64 } from "./audio";

describe("blobToBase64 / base64ToBlob", () => {
  it("round-trips arbitrary bytes through base64", async () => {
    const original = new Uint8Array([0, 1, 2, 253, 254, 255, 42, 128]);
    const blob = new Blob([original], { type: "audio/wav" });

    const base64 = await blobToBase64(blob);
    const roundTripped = base64ToBlob(base64, "audio/wav");

    expect(roundTripped.type).toBe("audio/wav");
    const bytes = new Uint8Array(await roundTripped.arrayBuffer());
    expect(Array.from(bytes)).toEqual(Array.from(original));
  });

  it("blobToBase64 omits the data-URL prefix", async () => {
    const blob = new Blob(["hello"], { type: "text/plain" });

    const base64 = await blobToBase64(blob);

    expect(base64.startsWith("data:")).toBe(false);
    expect(base64ToBlob(base64, "text/plain")).toBeInstanceOf(Blob);
  });
});
