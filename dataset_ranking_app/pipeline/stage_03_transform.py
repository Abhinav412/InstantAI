import pandas as pd
import numpy as np
import ast
import operator as op


SAFE_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv
}


def eval_formula(expr, variables):
    """
    Safely evaluate math expressions like:
    publications / student_faculty_ratio
    """

    def _eval(node):
        if isinstance(node, ast.BinOp):
            return SAFE_OPS[type(node.op)](
                _eval(node.left),
                _eval(node.right)
            )
        elif isinstance(node, ast.Name):
            return variables[node.id]
        elif isinstance(node, ast.Constant):
            return node.value
        else:
            raise ValueError("Unsafe expression")

    return _eval(ast.parse(expr, mode="eval").body)


def apply_feature_transforms(df: pd.DataFrame, feature_definitions):
    feature_df = pd.DataFrame()

    for feature in feature_definitions:

        if feature.transform == "log":
            col = feature.source_columns[0]
            feature_df[feature.feature_name] = np.log1p(df[col])

        elif feature.transform == "inverse":
            col = feature.source_columns[0]
            feature_df[feature.feature_name] = 1 / (df[col] + 1e-6)

        elif feature.transform == "formula":
            variables = {
                col: df[col].astype(float)
                for col in feature.source_columns
            }
            feature_df[feature.feature_name] = eval_formula(
                feature.formula, variables
            )

        elif feature.transform is None:
            col = feature.source_columns[0]
            feature_df[feature.feature_name] = df[col].astype(float)

        else:
            raise ValueError(f"Unknown transform: {feature.transform}")

    return feature_df
