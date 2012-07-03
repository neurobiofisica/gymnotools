TEMPLATE = subdirs
SUBDIRS = common commongui dsfmt dtcwpt paramchooser slice spikes svm winview

commongui.depends = common
paramchooser.depends = commongui
slice.depends = common
spikes.depends = common
winview.depends = commongui
