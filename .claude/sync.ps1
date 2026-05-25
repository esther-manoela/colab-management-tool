Set-Location "D:\Esther\Claude Code\Colab. Management Tool"
git add -A
$staged = git diff --cached --name-only
if ($staged) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    git commit -m "Auto-sync: $timestamp"
    git push
}
