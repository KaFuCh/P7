from xml.etree.ElementTree import parse


def create_global_decl():
    """
    A stub.
    Creates a global declaration to be inserted in UPPAAL XML
    :return: a string defining the global declarations
    """

    d = " // Place global declarations here. "
    return d


def create_system_decl():
    """
    A stub.
    Creates a system declaration to be inserted into UPPAAL XML
    :return: a string defining the system declaration
    """

    s = " System "
    return s


def create_model_xml(file, replace_dict, new_file):
    """
    XML: Updates the text of elements that are direct children of root
    :param file: path to xml file needing an update.
    :param replace_dict: A dictionary where the keys correspond to tags in the XML,
     and values containing new text to be placed in specified tags.
    :param new_file: path specifying where the updated file should be written to.
    """
    tree = parse(file)

    for key, value in replace_dict.items():
        element = tree.find(key)
        element.text = value

    tree.write(new_file)
