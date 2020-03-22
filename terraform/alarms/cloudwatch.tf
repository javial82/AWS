resource "aws_cloudwatch_metric_alarm" "billing_alarms" {
  for_each                  = var.billing_alarms
  alarm_name                = each.key
  comparison_operator       = "GreaterThanThreshold"
  evaluation_periods        = "1"
  metric_name               = "EstimatedCharges"
  namespace                 = "AWS/Billing"
  period                    = "21600"
  statistic                 = "Maximum"
  threshold                 = each.value
  alarm_description         = "Alarm for ${each.value}$ threshold."
  alarm_actions             = ["${aws_sns_topic.notify_me.arn}"]
  insufficient_data_actions = []
  dimensions = {
    Currency = "USD"
  }
  datapoints_to_alarm = 1
}
