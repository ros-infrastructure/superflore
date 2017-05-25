
class metadata_xml(object):
    """
    Basic definition of a metadata.xml file.
    """

    def __init__(self):
        self.is_person = True
        self.email = "hunter@openrobotics.org"
        self.name = "Hunter L. Allen"
        self.upstream_maintainer = None
        self.upstream_name = None
        self.upstream_email = None
        self.upstream_bug_url = None

    def get_metadata_text(self):
        ret  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        ret += "<!DOCTYPE pkgmetadata SYSTEM \"http://www.gentoo.org/dtd/metadata.dtd\">\n"
        ret += "<pkgmetadata>\n"
        ret += "  <maintainer type=\"" + self.maintainer_type + "\">\n"
        ret += "    <email>" + self.email + "</email>\n"
        ret += "    <name>" + self.name + "</name>\n"
        ret += "  </maintainer>\n"
        ret += "  <upstream>\n"
        ret += "    <maintainer status=\"active\">\n"
        ret += "      <email>" + self.upstream_email + "</email>\n"
        ret += "      <name>" + self.upstream_name + "</name>\n"
        ret += "    </maintainer>\n"
        ret += "    <bugs-to>" + self.upstream_bug_url + "</bugs-to>\n"
        ret += "  </upstream>\n"
        ret += "</pkgmetadata>\n"

        return ret
