from ConfigParser import SafeConfigParser
from utils import check_create_folder, download_from_url

# Import and set logger
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def download_all_files(species_ini_file):
    """
    Reads config INI file for a species, which contains the files (and
    their locations, or URLs) that must be loaded for this species, and calls
    the download_from_url function for each of those files.

    Arguments:
    species_ini_file -- Path to the particular species INI file. This
    is a string.

    Returns:
    Nothing, just downloads and saves files to download_folder

    """

    species_file = SafeConfigParser()
    species_file.read(species_ini_file)

    if species_file.has_section('GO'):
        if species_file.getboolean('GO', 'DOWNLOAD'):
            go_dir = species_file.get('GO', 'DOWNLOAD_FOLDER')
            check_create_folder(go_dir)

            obo_url = species_file.get('GO', 'GO_OBO_URL')
            download_from_url(obo_url, go_dir)

            goa_url = species_file.get('GO', 'ASSOC_FILE_URL')
            download_from_url(goa_url, go_dir)

    if species_file.has_section('KEGG'):
        if species_file.getboolean('KEGG', 'DOWNLOAD'):

            kegg_dir = species_file.get('KEGG', 'DOWNLOAD_FOLDER')
            check_create_folder(kegg_dir)

            kegg_root_url = species_file.get('KEGG', 'KEGG_ROOT_URL')

            kegg_info_url = kegg_root_url + species_file.get('KEGG',
                                                             'DB_INFO_URL')
            download_from_url(kegg_info_url, kegg_dir, 'kegg_db_info')

            all_set_urls = [kegg_root_url + x.strip() for x in species_file.get(
                    'KEGG', 'SETS_TO_DOWNLOAD').split(',')]

            for kegg_set_url in all_set_urls:
                download_from_url(kegg_set_url, kegg_dir)

    if species_file.has_section('DO'):
        if species_file.getboolean('DO', 'DOWNLOAD'):
            do_dir = species_file.get('DO', 'DOWNLOAD_FOLDER')
            check_create_folder(do_dir)

            obo_url = species_file.get('DO', 'DO_OBO_URL')
            download_from_url(obo_url, do_dir)

            mim2gene_url = species_file.get('DO', 'MIM2GENE_URL')
            download_from_url(mim2gene_url, do_dir)

            # The genemap_file needs a special Secret Key, which must be
            # retrieved from the secrets file if the user wishes to download
            # the genemap_file
            genemap_url = species_file.get('DO', 'GENEMAP_URL')

            secrets_location = species_file.get('species_info', 'SECRETS_FILE')
            secrets_file = SafeConfigParser()
            secrets_file.read(secrets_location)

            if not secrets_file.has_section('OMIM API secrets'):
                logger.error('Secrets file has no "OMIM API secrets" section,'
                             'which is required to download the genemap file '
                             ' to process Disease Ontology.')
                sys.exit(1)

            omim_secret_key = secrets_file.get('OMIM API secrets',
                                               'SECRET_KEY')
            genemap_url = genemap_url.replace('<SecretKey>', omim_secret_key)

            download_from_url(genemap_url, do_dir)


def download_kegg_info_files(kegg_set_ids, species_ini_file):
    """
    This is a KEGG-specific function that downloads the files containing
    information about the KEGG sets, such as their title, abstract, supporting
    publications, etc.

    Arguments:
    kegg_set_ids -- List of kegg set identifiers (e.g. hsa00010) for which
    info files will be downloaded.

    species_ini_file -- Path to the species INI config file. This
    is a string.

    Returns:
    Nothing, just downloads and saves files to download_folder

    """
    species_file = SafeConfigParser()
    species_file.read(species_ini_file)

    download_folder = species_file.get('KEGG', 'KEGGSET_INFO_FOLDER')
    check_create_folder(download_folder)

    full_info_url = species_file.get('KEGG', 'KEGG_ROOT_URL') + \
        species_file.get('KEGG', 'SET_INFO_DIR')

    for kegg_id in kegg_set_ids:
        kegg_info_file = full_info_url + kegg_id
        download_from_url(kegg_info_file, download_folder)
