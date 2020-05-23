#About
**listurls** extracts URLs from a directory of files.

#Usage
```
Usage: python3 -B ./listurls.py [FLAGS]
    --path:       Base path of the project to be scanned (Default: .)
    --root:       Root path of the project to be scanned (Default: /)
    --prefix:     Replace root path with this prefix (Default: /)
    --extensions: File extensions that are processed (Default: .html.htm.c.h.hpp.hxx.cc.cpp.c++.cxx.java.cs.txt)
    --exclude:    Paths of folders to exclude (Default: [])
    --output:     Path to output file (Default: ./output.txt)
    --backup:     Bookmark backup format (title, add_date, last_modified, url) default=False)
```

# Example

```
python3 -B listurls.py --path ./input --output ./urls.txt --backup
```