TEMPLATE = subdirs
SUBDIRS = common commongui crosspat dsfmt dtcwpt features paramchooser slice storms svm svmtool winview

commongui.depends = common
crosspat.depends = common
features.depends = common dtcwpt
paramchooser.depends = commongui
slice.depends = common dsfmt
storms.depends = common
svmtool.depends = common svm
winview.depends = commongui
