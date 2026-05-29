# Cyber-Range-Lab — Terraform-Konfiguration
# Version: 0.1 (Pilot)
# Provider: Hetzner Cloud (hcloud)
# Backend: lokal (fuer Pilot, spaeter S3/PostgreSQL)

terraform {
  required_version = ">= 1.7"
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.49"
    }
  }
}

provider "hcloud" {
  token = var.hcloud_token
}
