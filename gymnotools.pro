TEMPLATE = subdirs
SUBDIRS = common commongui dsfmt dtcwpt paramchooser svm

commongui.depends = common
paramchooser.depends = commongui
