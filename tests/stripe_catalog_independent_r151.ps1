param(
    [Parameter(Mandatory = $true)]
    [string]$Snapshot,
    [Parameter(Mandatory = $true)]
    [string]$Report
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$source = Get-Content -LiteralPath $Snapshot -Raw -Encoding UTF8 | ConvertFrom-Json
$expected = Get-Content -LiteralPath $Report -Raw -Encoding UTF8 | ConvertFrom-Json
if ($source.schema -ne "tristan-stripe-catalog-priv-r151-v1") { throw "UNSUPPORTED_SOURCE" }
if ($expected.schema -ne "tristan-stripe-catalog-audit-r151-v1") { throw "UNSUPPORTED_REPORT" }
if ($source.livemode -ne $true) { throw "NOT_LIVE_SNAPSHOT" }

$listedProducts = @($source.products)
$listedPrices = @($source.prices)
$extraProducts = @($source.supplemental_products)
$extraPrices = @($source.supplemental_prices)
$links = @($source.links)
$allProducts = @($listedProducts) + @($extraProducts)
$allPrices = @($listedPrices) + @($extraPrices)
$pmap = [System.Collections.Generic.Dictionary[string,object]]::new([System.StringComparer]::Ordinal)
$pricemap = [System.Collections.Generic.Dictionary[string,object]]::new([System.StringComparer]::Ordinal)

foreach ($p in $allProducts) {
    if ($pmap.ContainsKey([string]$p.id)) { throw "DUPLICATE_PRODUCT" }
    $pmap.Add([string]$p.id, $p)
}
foreach ($p in $allPrices) {
    if ($pricemap.ContainsKey([string]$p.id)) { throw "DUPLICATE_PRICE" }
    $pricemap.Add([string]$p.id, $p)
}
if ($listedProducts.Count -ne [int]$source.discovery.list_products_count) { throw "LIST_COUNT_MISMATCH" }
if ($listedPrices.Count -ne [int]$source.discovery.list_prices_count) { throw "PRICE_COUNT_MISMATCH" }
if ($links.Count -ne 23) { throw "EXPECTED_LINK_COVERAGE_MISSING" }

$activeLinks = @($links | Where-Object { $_.active -eq $true })
$activeProducts = @($allProducts | Where-Object { $_.active -eq $true })
$inactiveOrMissingProduct = 0
$inactiveOrMissingPrice = 0
$heldLiveLinks = 0
$linkPriceMismatch = 0
$allLineItemsCount = 0
$activeLinkedProductIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
foreach($l in $links) {
    if ($l.line_item_status -ne "VERIFIED_COMPLETE") { throw "LINE_STATUS_NOT_VERIFIED" }
    $entries = @($l.line_items)
    if ($entries.Count -lt 1) { throw "MISSING_LINE" }
    $allLineItemsCount += $entries.Count
    if ($l.active -ne $true) { continue }
    foreach($entry in $entries) {
        $productKey = [string]$entry.product_id
        $priceid = [string]$entry.price_id
        if (-not $pmap.ContainsKey($productKey)) { $inactiveOrMissingProduct++; continue }
        if (-not $pricemap.ContainsKey($priceid)) { $inactiveOrMissingPrice++; continue }
        $p = $pmap[$productKey]
        $price = $pricemap[$priceid]
        if ($p.active -ne $true) { $inactiveOrMissingProduct++ }
        if ($price.active -ne $true) { $inactiveOrMissingPrice++ }
        if ($price.product_id -cne $productKey) { $linkPriceMismatch++ }
        if ($p.active -eq $true) { [void]$activeLinkedProductIds.Add($productKey) }
        $readiness = ""
        $stage = ""
        if ($null -ne $p.metadata) {
            $fields = @($p.metadata.PSObject.Properties | ForEach-Object { $_.Name })
            if ($fields -contains "readiness") { $readiness = [string]$p.metadata.readiness }
            if ($fields -contains "stage") { $stage = [string]$p.metadata.stage }
        }
        if ($readiness -match "HOLD" -or $stage -match "HOLD") { $heldLiveLinks++ }
    }
}
$missingDefault = @($activeProducts | Where-Object { -not $_.default_price }).Count
$notLinked = @($activeProducts | Where-Object { -not $activeLinkedProductIds.Contains([string]$_.id) }).Count
$taxDisabled = @($activeLinks | Where-Object { $_.automatic_tax_enabled -ne $true }).Count

$actual = @{
    listed_products = $listedProducts.Count
    listed_prices = $listedPrices.Count
    direct_confirmed_additional_products = $extraProducts.Count
    direct_confirmed_additional_prices = $extraPrices.Count
    identified_products_at_least = $allProducts.Count
    identified_prices_at_least = $allPrices.Count
    payment_links_checked = $links.Count
    link_line_items_checked = $allLineItemsCount
    active_links = $activeLinks.Count
    hold_links = $heldLiveLinks
    active_without_default_price = $missingDefault
    active_without_active_link = $notLinked
    tax_auto_disabled_links = $taxDisabled
}
$compare = @{
    listed_products = [int]$expected.coverage.listed_products
    listed_prices = [int]$expected.coverage.listed_prices
    direct_confirmed_additional_products = [int]$expected.coverage.direct_confirmed_additional_products
    direct_confirmed_additional_prices = [int]$expected.coverage.direct_confirmed_additional_prices
    identified_products_at_least = [int]$expected.coverage.identified_products_at_least
    identified_prices_at_least = [int]$expected.coverage.identified_prices_at_least
    payment_links_checked = [int]$expected.coverage.payment_links_checked
    link_line_items_checked = [int]$expected.coverage.link_line_items_checked
    active_links = [int]$expected.observations.active_payment_links
    hold_links = [int]$expected.observations.active_links_to_products_with_hold_metadata
    active_without_default_price = [int]$expected.observations.active_products_without_default_price
    active_without_active_link = [int]$expected.observations.active_products_without_active_link
    tax_auto_disabled_links = [int]$expected.observations.active_links_with_automatic_tax_disabled
}
foreach($k in $actual.Keys) {
    if ($actual[$k] -ne $compare[$k]) { throw "RECONCILIATION_COUNT_MISMATCH" }
}
if ($inactiveOrMissingProduct -ne 0 -or $inactiveOrMissingPrice -ne 0 -or $linkPriceMismatch -ne 0) {
    throw "UNRESOLVED_ACTIVE_SALE_REFERENCES"
}
if ($allProducts.Count -lt $listedProducts.Count + $extraProducts.Count) {
    throw "INTERNAL_COUNT_ERROR"
}
if ($expected.coverage.completeness -ne "NOT_PROVEN") {
    throw "EXHAUSTIVENESS_FALSE_CERTAINTY"
}
Write-Output "INDEPENDENT_PS_RECONCILIATION_PASS links=$($links.Count) identified_products_min=$($allProducts.Count) identified_prices_min=$($allPrices.Count) hold_links=$heldLiveLinks active_tax_disabled=$taxDisabled"
