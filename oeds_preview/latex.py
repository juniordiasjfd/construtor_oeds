# Install the library before running:
# pip install latex2mathml

import latex2mathml.converter
import bs4


def latex_to_mathml(latex_str: str) -> str:
    """
    Convert a LaTeX math expression to MathML.
    Args:
        latex_str (str): The LaTeX string to convert.
    Returns:
        str: MathML representation of the LaTeX input.
    """
    if not isinstance(latex_str, str) or not latex_str.strip():
        raise ValueError("Input must be a non-empty LaTeX string.")
    try:
        mathml_output = latex2mathml.converter.convert(latex_str)
        mathml_output = mathml_output.replace('display="inline"', 'displaystyle="true"')
        return mathml_output
    except Exception as e:
        raise RuntimeError(f"Failed to convert LaTeX to MathML: {e}")
def html_with_latex_class_2_html_with_mathml(soup:bs4.BeautifulSoup):
    equacoes = soup.find_all(attrs={'class':'latex'})
    for eq in equacoes:
        mathml_tag = bs4.BeautifulSoup(latex_to_mathml(eq.get_text()), 'html.parser')
        eq.insert_before(mathml_tag)
        eq.decompose()
    return soup
if __name__ == "__main__":
    # Example LaTeX input
    latex_input = r"\frac{a^2 + b^2}{c^2}"

    soup = bs4.BeautifulSoup('<p>This library <span>provides</span> a <strong>simple</strong> and <span class="latex">a^2 + b^2 = c^2</span> efficient way to perform the <span class="latex">\\frac12</span> conversion.</p>', 'html.parser')
    equacoes = soup.find_all(attrs={'class':'latex'})
    for eq in equacoes:
        mathml_tag = bs4.BeautifulSoup(latex_to_mathml(eq.get_text()), 'html.parser')
        eq.insert_before(mathml_tag)
        eq.insert_before(' ')
        eq.decompose()
    try:
        mathml_result = latex_to_mathml(latex_input)
        print("LaTeX Input:", latex_input)
        print("\nMathML Output:\n", mathml_result)
    except Exception as err:
        print("Error:", err)
