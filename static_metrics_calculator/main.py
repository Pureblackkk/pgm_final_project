from info_metrics import InfoMetricsCalculator
from user_metrics import UserMetricsCalculator

if __name__ == '__main__':
    staticCal = InfoMetricsCalculator('../../data/database/')
    staticCal.infoFeature()
    staticCal.save('../../data/database/')
    
    staticCal = UserMetricsCalculator('../../data/database/')
    staticCal.userFeature()
    staticCal.save('../../data/database_after_static/')


