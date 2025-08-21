# Windows Firewall Setup for Production
# Run this script as Administrator

Write-Host "🔥 Configuring Windows Firewall for Galveston Reservation System..." -ForegroundColor Blue
Write-Host ""

# Remove any existing rules to avoid conflicts
Write-Host "🧹 Cleaning up old firewall rules..."
try {
    Remove-NetFirewallRule -DisplayName "*Galveston*" -ErrorAction SilentlyContinue
    Write-Host "✅ Old rules cleaned up" -ForegroundColor Green
} catch {
    Write-Host "ℹ️  No old rules to clean up" -ForegroundColor Gray
}

Write-Host ""

# Add HTTP rule for port 8080 (for Cloudflare proxy)
Write-Host "📝 Adding HTTP rule (port 8080 - Cloudflare proxy)..."
try {
    New-NetFirewallRule -DisplayName "Galveston Reservation HTTP" -Direction Inbound -Port 8080 -Protocol TCP -Action Allow -Profile Any -Enabled True
    Write-Host "✅ Port 8080 rule added successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to add port 8080 rule: $($_.Exception.Message)" -ForegroundColor Red
}

# Optional: Add rule for port 5000 (Flask development)
Write-Host "📝 Adding development rule (port 5000 - Flask dev server)..."
try {
    New-NetFirewallRule -DisplayName "Galveston Reservation Dev" -Direction Inbound -Port 5000 -Protocol TCP -Action Allow -Profile Any -Enabled True
    Write-Host "✅ Port 5000 rule added successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to add port 5000 rule: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔍 Verifying firewall rules..."

# Display the rules we just created
try {
    $rules = Get-NetFirewallRule -DisplayName "*Galveston*" | Select-Object DisplayName, Direction, Action, Enabled
    $rules | Format-Table -AutoSize
} catch {
    Write-Host "⚠️  Could not retrieve firewall rules" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Windows Firewall configured successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Your server is now ready for Cloudflare at str.ptpsystem.com" -ForegroundColor Cyan
