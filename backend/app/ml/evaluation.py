"""
Evaluation metrics computation for crop stress models.
"""
from typing import Dict, Any, List
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)


def evaluate_model(
    model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    class_names: List[str],
    feature_names: List[str]
) -> Dict[str, Any]:
    """
    Compute comprehensive classification metrics and feature importances.
    """
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="macro", zero_division=0)
    
    cm = confusion_matrix(y_test, y_pred, labels=class_names).tolist()
    
    report_dict = classification_report(
        y_test,
        y_pred,
        target_names=class_names,
        output_dict=True,
        zero_division=0
    )
    
    # Feature importances from Random Forest
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        feature_importance_list = [
            {"feature": name, "importance": round(float(imp), 4)}
            for name, imp in zip(feature_names, importances)
        ]
        # Sort descending
        feature_importance_list.sort(key=lambda x: x["importance"], reverse=True)
    else:
        feature_importance_list = []

    return {
        "accuracy": round(float(acc), 4),
        "precision_macro": round(float(prec), 4),
        "recall_macro": round(float(rec), 4),
        "f1_macro": round(float(f1), 4),
        "confusion_matrix": cm,
        "classification_report": report_dict,
        "feature_importance": feature_importance_list,
        "class_names": class_names,
        "feature_names": feature_names
    }
