# nexus2aci

Goal of this project is to take a Nexus 7k/5k config and turn it into ACI configuration

# How to use

## Basic configuration: 
* Get show run from Nexus switches and save each of them in a text file inside the config/ folder
* Fill out `filelist.py` adding the files you created before, following this example: \
`entiredc = {'agg': ['config/AGGSNANGDC-1.nxos', 'config/AGGSNANGDC-2.nxos'],` \
`{'Cage1': ['config/Cage1-1.nxos', 'config/Cage2-2.nxos']}` \
"agg" and "Cage1" are arbitrary nicknames given to the nexus pair


## filelist.py
### Run the script
* Complete basic configuration
* Run `parse_conf.py`

You will get two files, tempdata.bin and intnames.csv. The first is a binary file containing the representation of all interfaces in the fabric and will be used in the later steps. The second contains the names and descriptions of all interfaces. This is a sample output:

| name                    | description | newname |
|-------------------------|-------------|---------|
| agg/1/Ethernet100/1/1   | SVPROD01 |         |
| Cage1/1/port-channel100 | SVPROD02 |         |
| Cage1/vpc-123 | SVPROD34 | |

The file will not contain port-channels that are members of a VPC, as these objects are unnecessary in APIC and we only need the VPC Policy Group

Interface names are formatted as such:

| nexus pair nick | switch number | interface |
| --- | --- | ---|
| agg | 1 | Ethernet100/1/1 |
| Cage1 | 1 | port-channel100 |
| Cage1 | vpc-123| |

Switch number is given by the order of the config files inside `filelist.py`

VPCs are one levle higher as they exist in the entire nexus pair, not just one machine.

### Fill out the file
Fill out filelist.py adding the new interface names in the "newname" column. \

Do not touch the first column. You may delete lines if you won't need those interfaces. \Lines with a blank "newname" field will not be imported in tha later step.

**Formatting** \
Ethernet interfaces can be expressed in four ways:
* Single interfaces: `100/1/1` (leaf/card/port)
* Interface ranges: `100/1/1-5`
* Leaf pairs: `100,150/1/1`
* A combination of leaf pairs and interface ranges: `100,150/1/1-5`

Port channels and VPCs must only be filled out with a name, without specifying leaf and card

## generate_excel.py
* Complete basic configuration
* *(Optional)* Edit, the `epg()`, `anp()`, `bd()`, `vrf()` and `tenant()` functions to pre-generate object names in the output file.
* Run `generate_excel.py`
* Open `excelout.xlsx` and fill in the form or delete unused VLANs

## excelreader.py
* Run all previous steps
* Fill out `policymappings.py` with the names of your LACP policy profiles. Do NOT edit the dictionary keys
* Fill out `defaults.py`, especially "POLICY_GROUP_ACCESS". Change it into the default policy group name for access interfaces. Change the rest as you see fit.
* Insert APIC credentials in `acicreds.py`
* Create one Leaf Profile containing one Interface Selector Profile for every leaf and leaf pair.
* Make sure the output files from previous steps are in the main folder and with the correct names
* Cross your fingers
* Run the script