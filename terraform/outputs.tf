# Set these as nameservers in Namecheap for cachemeifyoucan.dev
output "route53_nameservers" {
  value = aws_route53_zone.main.name_servers
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.site.id
}

output "cloudfront_domain" {
  value = aws_cloudfront_distribution.site.domain_name
}

output "certificate_arn" {
  value = aws_acm_certificate.site.arn
}

output "bucket_name" {
  value = aws_s3_bucket.site.id
}

output "stats_api_url" {
  value = aws_apigatewayv2_stage.stats.invoke_url
}
