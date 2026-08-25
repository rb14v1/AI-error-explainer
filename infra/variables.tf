variable "tenant_id" {
  description = "Tenant identifier used for cost allocation and incident attribution."
  type        = string
}

variable "submission_id" {
  description = "Submission identifier used for cost allocation and incident attribution."
  type        = string
}

variable "cost_centre" {
  description = "Cost centre code used for financial governance and chargeback."
  type        = string
}

variable "aws_region" {
  description = "AWS region in which resources are deployed."
  type        = string
  default     = "eu-west-1"
}
