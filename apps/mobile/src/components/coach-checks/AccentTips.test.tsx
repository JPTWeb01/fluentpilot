import { render } from "@testing-library/react-native";

import { AccentTips } from "./AccentTips";

describe("AccentTips", () => {
  it("renders nothing when there are no tips", () => {
    const { toJSON } = render(<AccentTips tips={[]} />);
    expect(toJSON()).toBeNull();
  });

  it("renders each tip's fields", () => {
    const { toJSON } = render(
      <AccentTips tips={[{ phrase: "think", tip: "Try the soft 'th' sound instead of 'tink'." }]} />
    );

    const tree = JSON.stringify(toJSON());
    expect(tree).toContain("think");
    expect(tree).toContain("Try the soft 'th' sound instead of 'tink'.");
  });
});
