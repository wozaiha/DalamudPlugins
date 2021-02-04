$translations = @{}
$index = 0
$en_desc = ""

Get-Content -Encoding UTF8 -Path translations.txt | ForEach-Object {
    $index++
    If ( $index % 2 -eq 0) {
        $translations.Add($en_desc, $_)
    }else{
        $en_desc = $_
    }
}

function Get-Name($value) {
    if ($translations.ContainsKey($value)) {
        $translations[$value]
    } else {
        $value
    }
}
echo $(Get-Name("Shows the current countdown time."))