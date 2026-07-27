import { render } from "@testing-library/react-native";

import { VocabularySuggestions } from "./VocabularySuggestions";

describe("VocabularySuggestions", () => {
  it("renders nothing when there are no suggestions", () => {
    const { toJSON } = render(<VocabularySuggestions suggestions={[]} />);
    expect(toJSON()).toBeNull();
  });

  it("renders each suggestion's fields", () => {
    const { toJSON } = render(
      <VocabularySuggestions
        suggestions={[
          { original: "desk", suggestion: "countertop", explanation: "More precise for a kitchen." },
        ]}
      />
    );

    const tree = JSON.stringify(toJSON());
    expect(tree).toContain("desk");
    expect(tree).toContain("countertop");
    expect(tree).toContain("More precise for a kitchen.");
  });
});
