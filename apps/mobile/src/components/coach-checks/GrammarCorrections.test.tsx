import { render } from "@testing-library/react-native";

import { GrammarCorrections } from "./GrammarCorrections";

describe("GrammarCorrections", () => {
  it("renders nothing when there are no corrections", () => {
    const { toJSON } = render(<GrammarCorrections corrections={[]} />);
    expect(toJSON()).toBeNull();
  });

  it("renders each correction's fields", () => {
    const { toJSON } = render(
      <GrammarCorrections
        corrections={[
          { original: "I goed", corrected: "I went", explanation: "Use the irregular past tense." },
        ]}
      />
    );

    const tree = JSON.stringify(toJSON());
    expect(tree).toContain("I goed");
    expect(tree).toContain("I went");
    expect(tree).toContain("Use the irregular past tense.");
  });
});
