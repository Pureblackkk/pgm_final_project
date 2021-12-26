from user_metrics import UserMetricsCalculator
from relation_metrics import RelationMetricsCalculator

if __name__ == '__main__':
    dynamicCal = RelationMetricsCalculator('../../data/database_after_static/')
    print(dynamicCal.getTextsimilarBetween('7659462358', '6628857952'))