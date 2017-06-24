"""
Generate the metadata.xml file for a package.
"""
class metadata_xml(object):
    def __init__(self):
        self.email = "hunter@openrobotics.org"
        self.name = "Hunter L. Allen"
        self.upstream_name = None
        self.upstream_email = None
        self.upstream_bug_url = None
        self.maintainer_type = "person"

    def get_metadata_text(self):
        ret = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        ret += "<!DOCTYPE pkgmetadata SYSTEM "
        ret += "\"http://www.gentoo.org/dtd/metadata.dtd\">\n"
        ret += "<pkgmetadata>\n"
        ret += "  <maintainer type=\"" + self.maintainer_type + "\">\n"
        ret += "    <email>" + self.email + "</email>\n"
        ret += "    <name>" + self.name + "</name>\n"
        ret += "  </maintainer>\n"
        if self.upstream_email is not None and self.upstream_name is not None:
            ret += "  <upstream>\n"
            ret += "    <maintainer status=\"active\">\n"
            ret += "      <email>" + self.upstream_email + "</email>\n"
            ret += "      <name>" + self.upstream_name + "</name>\n"
            ret += "    </maintainer>\n"
            if self.upstream_bug_url is not None:
                ret += "    <bugs-to>" + self.upstream_bug_url + "</bugs-to>\n"
            ret += "  </upstream>\n"
        ret += "</pkgmetadata>\n"
        return ret
