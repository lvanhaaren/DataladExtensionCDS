# DataLad CDS Extension

Extension for the automatic download from the CDS DataStore.
Works like `datalad download-url`


In general a command looks like this:

      datalad download-cds [-h] [-d PATH] [-O PATH] [-o] [--archive] [--nosave] [-m MESSAGE]
      [--version] filenames

Example:

    datalad download-cds test.txt -m "This is the commit message"

In this case test.txt contains a cds request.

    'derived-utci-historical',{
      'version': '1_1',
      'format': 'zip',
      'variable': 'universal_thermal_climate_index',
      'product_type': 'intermediate_dataset',
      'year': '2020',
      'month': '01',
      'day': '01',
    }, 'test4.zip'
You can generate yourself the request here:
https://cds.climate.copernicus.eu/cdsapp#!/search?type=dataset

## Options

### filename
This is the file, in which the cds request is stored

### -h, --help
Shows the help message, --help shows the man page

### -d PATH, --dataset PATH
Defines the dataset, not necessary to define

### --path PATH
If specified, overrides the PATH of where the file gets written to. If not specified, it has to be present in the cds-request-file

### -o, --overwrite

flag to overwrite it if target file exists.
### --archive
pass the downloaded files to datalad add-archive-content –delete.
### --nosave
by default all modifications to a dataset are immediately saved. Giving this option will disable this behavior.
### -m MESSAGE, --message MESSAGE
Message to be added to the git log
### --version

show the module and its version
