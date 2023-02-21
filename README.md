# DataLad CDS Extension

## Recommended Knowledge:

Datalad https://www.datalad.org/

## Set up
Clone this repository and run this command

    pip install -e .

Make sure you have valid credentials for the cds api!
If you're not registered yet, here is the manual:
https://cds.climate.copernicus.eu/user/register?destination=%2F%23!%2Fhome \
Create a datalad dataset:

    datalad create -c text2git DataLad-101
Change to the dataset:

    cd Datalad-101

Now you can execute the datalad-download-cds command!

Datalad handbook:
http://handbook.datalad.org/en/latest/

Datalad documentation:
https://docs.datalad.org/en/stable/index.html

## Usage
Extension for the automatic download from the CDS DataStore.
Works like `datalad download-url`


In general a command looks like this:

      datalad download-cds [-h] [-d PATH] [-O PATH] [--archive] [--nosave] [-m MESSAGE]
      [--version] filenames

Example:

    datalad download-cds test.txt -m "This is the commit message"


In this case test.txt contains a cds request.

    'derived-reanalysis-energy-moisture-budget',
        {
            'format': 'zip',
            'variable': 'divergence_of_vertical_integral_of_latent_heat_flux',
            'year': '1979',
            'month': '01',
            'area': [
                90, 0, -90,
                360,
            ],
        },
        'download.zip'

You can generate yourself the request here:
https://cds.climate.copernicus.eu/cdsapp#!/search?type=dataset

Example for a request generated by the CDS data store:

    import cdsapi

    c = cdsapi.Client()

    c.retrieve(
        'derived-reanalysis-energy-moisture-budget',
        {
            'format': 'zip',
            'variable': 'divergence_of_vertical_integral_of_latent_heat_flux',
            'year': '1979',
            'month': '01',
            'area': [
                90, 0, -90,
                360,
            ],
        },
        'download.zip')

### You only need the request in between the brackets of the retrieve method!

## Request Know-How

A request always consists of:

A dataset: 

`'derived-reanalysis-energy-moisture-budget'`

request-parameters (in form of a dictionary):

    {
        'format': 'zip',
        'variable': 'divergence_of_vertical_integral_of_latent_heat_flux',
        'year': '1979',
        'month': '01',
        'area': [
            90, 0, -90,
            360,
        ],
    }

A filename where the request will get written into:

`'download.zip'`

The first two parameters are mandatory! If you do not specify the file where it gets written into in the file of the general request, you have to do it in the command.

Example:

    datalad download-cds test.txt --path test2.zip

If you specify both, the path in the command will be used!

## Options

### filename
This is the file, in which the cds request is stored

### -h, --help
Shows the help message, --help shows the man page

### -d PATH, --dataset PATH
Defines the dataset, not necessary to define

### --path PATH, -O PATH
If specified, overrides the PATH of where the file gets written to. If not specified, it has to be present in the cds-request-file

### --archive
pass the downloaded files to datalad add-archive-content –delete.

### --nosave
by default all modifications to a dataset are immediately saved. Giving this option will disable this behavior.

### -m MESSAGE, --message MESSAGE
Message to be added to the git log

### --version
show the module and its version
