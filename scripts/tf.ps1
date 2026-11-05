param(
  [ValidateSet("fmt", "validate", "plan", "apply")]
  [string]$Action = "plan",
  [string]$Env = "dev"
)

$ErrorActionPreference = "Stop"
$env:AWS_PROFILE = "dip"
$root = Split-Path $PSScriptRoot -Parent
$envDir = "$root\infra\envs\$Env"

switch ($Action) {
  "fmt"      { terraform -chdir="$root\infra" fmt -recursive }
  "validate" { terraform -chdir=$envDir init -input=false; terraform -chdir=$envDir validate }
  "plan"     { terraform -chdir=$envDir plan -out=tfplan }
  "apply"    { terraform -chdir=$envDir apply tfplan }
}
