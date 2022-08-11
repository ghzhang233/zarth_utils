import logging
import os
import random
from collections import defaultdict

import numpy as np
import tensorflow as tf
import torch
from sklearn.metrics import roc_auc_score, confusion_matrix, accuracy_score, log_loss, f1_score, precision_score


def set_random_seed(seed, deterministic=False, no_torch=False, no_tf=False):
    """
    Set the random seed for the reproducibility. Environment variable CUBLAS_WORKSPACE_CONFIG=:4096:8 is also needed.
    :param seed: the random seed
    :type seed: int
    :param deterministic: whether use deterministic, slower is True, cannot guarantee reproducibility if False
    :param no_torch: if torch is not installed, set this True
    :param no_tf: if tensorflow is not installed, set this True
    :type deterministic: bool
    """
    random.seed(seed)
    np.random.seed(seed)
    if not no_torch:
        torch.manual_seed(seed)
        if deterministic:
            torch.backends.cudnn.benchmark = False
            torch.backends.cudnn.deterministic = True
    if not no_tf:
        tf.random.set_seed(seed)


def to_categorical(y, num_classes=None, dtype='float32'):
    """Converts a class vector (integers) to binary class matrix.
    E.g. for use with `categorical_crossentropy`.
    Args:
        y: Array-like with class values to be converted into a matrix
            (integers from 0 to `num_classes - 1`).
        num_classes: Total number of classes. If `None`, this would be inferred
          as `max(y) + 1`.
        dtype: The data type expected by the input. Default: `'float32'`.
    Returns:
        A binary matrix representation of the input. The class axis is placed
        last.
    """
    y = np.array(y, dtype='int')
    input_shape = y.shape
    if input_shape and input_shape[-1] == 1 and len(input_shape) > 1:
        input_shape = tuple(input_shape[:-1])
    y = y.ravel()
    if not num_classes:
        num_classes = np.max(y) + 1
    n = y.shape[0]
    categorical = np.zeros((n, num_classes), dtype=dtype)
    categorical[np.arange(n), y] = 1
    output_shape = input_shape + (num_classes,)
    categorical = np.reshape(categorical, output_shape)
    return categorical


def get_classical_metrics(y_true, y_pred, y_prob, sample_weight=None):
    """
    Return all the metrics including utility and fairness
    :param y_true: ground truth labels
    :type y_true: [n, ]
    :param y_pred: the predicted labels
    :type y_pred: [n, ]
    :param y_prob: the predicted scores
    :type y_prob: [n, classes] or [n, ]
    :param sample_weight: sample weights
    """
    assert len(np.unique(y_true)) >= 2  # there should be at least two classes
    assert len(y_pred.shape) == 1 or (len(y_pred.shape) == 2 and y_pred.shape[1] == 1)  # y_pred must be [n, ] or [n, 1]
    assert len(y_true.shape) == 1 or (len(y_true.shape) == 2 and y_true.shape[1] == 1)  # y_true must be [n, ] or [n, 1]
    y_true = y_true.reshape([-1])
    y_pred = y_pred.reshape([-1])
    num_classes = len(np.unique(y_true))

    if len(y_prob.shape) == 2 and y_prob.shape[1] == 1:  # y_prob can be [n, ] or [n, c]
        y_prob = y_prob.reshape([-1])

    ret = defaultdict()
    ret["ACC"] = accuracy_score(y_true=y_true, y_pred=y_pred, sample_weight=sample_weight)

    if num_classes == 2:
        ret["TNR"], ret["FPR"], ret["FNR"], ret["TPR"] = confusion_matrix(y_true, y_pred, normalize="true",
                                                                          sample_weight=sample_weight).ravel()
        ret["Precision"] = precision_score(y_true, y_pred, sample_weight=sample_weight)
        ret["F1"] = f1_score(y_true=y_true, y_pred=y_pred, sample_weight=sample_weight)
        ret["PO1"] = (y_pred == 1).sum() / len(y_pred)

    if len(y_prob.shape) == 2:
        ret["Loss"] = log_loss(y_true=to_categorical(y_true), y_pred=y_prob, sample_weight=sample_weight)
        ret["AUC"] = roc_auc_score(y_true=to_categorical(y_true), y_score=y_prob, sample_weight=sample_weight)
    else:
        ret["Loss"] = log_loss(y_true=y_true, y_pred=y_prob, sample_weight=sample_weight)
        ret["AUC"] = roc_auc_score(y_true=y_true, y_score=y_prob, sample_weight=sample_weight)

    return ret


def to_device(_v, device):
    if _v is None:
        return _v
    if type(_v) in [tuple, list]:
        return [to_device(i, device) for i in _v]
    else:
        return _v.to(device)


def torch_save(obj, f, **kwargs):
    """
    Save the obj into f. The only difference is this function will save only when  f dose not exist.
    :param obj: the object to be saved
    :param f: the saving path
    :type f: str
    :param kwargs: parameters to torch.save
    """
    assert type(f) == str
    if os.path.exists(f):
        raise ValueError
    torch.save(obj=obj, f=f, **kwargs)


def save_checkpoint(path_save, **kwargs):
    checkpoint = {k: kwargs[k].state_dict() for k in kwargs if kwargs[k] is not None}
    torch_save(checkpoint, path_save)


def load_checkpoint(path_load, **kwargs):
    checkpoint = torch.load(path_load)
    for k in kwargs:
        assert k in checkpoint.keys()
        kwargs[k].load_state_dict(checkpoint[k])


class EarlyStoppingManager:
    def __init__(self, path_best_model, max_no_improvement=10, greater_is_better=True):
        self.greater_is_better = greater_is_better
        self.max_no_improvement = max_no_improvement
        self.path_best_model = path_best_model

        self.best_score = None
        self.best_epoch = None
        self.no_improvement = None
        self.reset()

    def reset(self):
        self.no_improvement = 0
        self.best_score = -np.inf
        self.best_epoch = None

    def _sign(self):
        if self.greater_is_better:
            return 1
        else:
            return -1

    def get_best_score(self):
        return self.best_epoch * self._sign()

    def __call__(self, score, epoch=None, **kwargs):
        assert self.no_improvement < self.max_no_improvement, "Should Be Stopped!"
        if score * self._sign() > self.best_score:
            self.no_improvement = 0
            self.best_score = score * self._sign()
            self.best_epoch = epoch
            save_checkpoint(self.path_best_model, early_stop_manager=self, **kwargs)
            return False
        else:
            self.no_improvement += 1
            if self.no_improvement == self.max_no_improvement:
                logging.info("Early Stop at Epoch %d with Score %.3lf." % (self.best_epoch, self.get_best_score()))
                return True

    def state_dict(self):
        return {
            "greater_is_better": self.greater_is_better,
            "max_no_improvement": self.max_no_improvement,
            "best_score": self.best_score,
            "best_epoch": self.best_epoch,
            "no_improvement": self.no_improvement
        }

    def load_state_dict(self, state):
        self.greater_is_better = state["greater_is_better"]
        self.max_no_improvement = state["max_no_improvement"]
        self.best_score = state["best_score"]
        self.best_epoch = state["best_epoch"]
        self.no_improvement = state["no_improvement"]
