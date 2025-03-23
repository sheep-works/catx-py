$pubdir = "./publish"
if ((Test-Path $pubdir) -eq $false) {
    mkdir $pubdir
} else {
    Remove-Item -Recurse $pubdir
    mkdir $pubdir
}

copy-item -force ./dist/main.exe -Destination ./

Copy-Item -Force ./main.exe -Destination $pubdir
Copy-Item -Force .\README.pdf -Destination $pubdir
Copy-Item -Recurse -Force .\configs -Destination $pubdir
copy-item -Recurse -force .\scripts -Destination $pubdir
mkdir $pubdir/source
mkdir $pubdir/result

Compress-Archive -Force -path $pubDir -DestinationPath "publish.zip"
