import { render } from "@testing-library/react-native";

import { PronunciationTips } from "./PronunciationTips";

describe("PronunciationTips", () => {
  it("renders nothing when there are no tips", () => {
    const { toJSON } = render(<PronunciationTips tips={[]} />);
    expect(toJSON()).toBeNull();
  });

  it("renders each tip's fields", () => {
    const { toJSON } = render(
      <PronunciationTips tips={[{ word: "comfortable", tip: "Often mispronounced as four syllables." }]} />
    );

    const tree = JSON.stringify(toJSON());
    expect(tree).toContain("comfortable");
    expect(tree).toContain("Often mispronounced as four syllables.");
  });
});
