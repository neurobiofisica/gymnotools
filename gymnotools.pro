TEMPLATE = subdirs
SUBDIRS = common commongui dsfmt dtcwpt paramchooser spikes svm winview

commongui.depends = common
paramchooser.depends = commongui
spikes.depends = common
winview.depends = commongui
