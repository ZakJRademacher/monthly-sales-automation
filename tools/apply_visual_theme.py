"""Apply the approved sales dashboard layout to a generated workbook."""
from tableau_layout import apply
def apply_theme(path):
    apply(path,'sales')
    return path
