APIVERSION?=xen-api-v5
LIB_FILES:=__init__.py common.py
DESTDIR?=/
SCRIPTDIR?=/usr/libexec/xapi-storage-script
PYTHONDIR?=/usr/lib/python2.7/site-packages/xapi/storage/linstor

PROJECT_NAME=linstor-xen
LATESTTAG=$(shell git describe --abbrev=0 --tags | tr -d 'v')
SOURCES := $(wildcard lib/linstor/*.py)
SOURCES += $(wildcard xen-api-v5/*.py)
SOURCES += Makefile $(PROJECT_NAME).spec

.PHONY: clean
clean:

install:
	#################################
	@echo "# Installing shared Python code #"
	#################################
	mkdir -p $(DESTDIR)$(PYTHONDIR)
	cd lib/linstor && install -m 0755 $(LIB_FILES) $(DESTDIR)$(PYTHONDIR)/
	##############################
	@echo "# Installing datapath plugin #"
	##############################
	mkdir -p $(DESTDIR)$(SCRIPTDIR)/datapath/linstor/
	cd $(APIVERSION) && install -m 0755 plugin.py datapath.py $(DESTDIR)$(SCRIPTDIR)/datapath/linstor
	cd $(DESTDIR)$(SCRIPTDIR)/datapath/linstor; for link in Datapath.attach Datapath.activate Datapath.deactivate Datapath.detach Datapath.open Datapath.close; do if ! test -L $$link; then ln -s datapath.py $$link; fi; done
	cd $(DESTDIR)$(SCRIPTDIR)/datapath/linstor; for link in Plugin.query Plugin.diagnostics Plugin.ls; do if ! test -L $$link; then ln -s plugin.py $$link; fi; done
	###############################
	@echo "# Installing volume/SR plugin #"
	###############################
	mkdir -p $(DESTDIR)$(SCRIPTDIR)/volume/org.xen.xapi.storage.linstor/
	cd $(APIVERSION) && install -m 0755 plugin.py volume.py sr.py $(DESTDIR)$(SCRIPTDIR)/volume/org.xen.xapi.storage.linstor
	cd $(DESTDIR)$(SCRIPTDIR)/volume/org.xen.xapi.storage.linstor; for link in Volume.clone Volume.create Volume.destroy Volume.resize Volume.set Volume.set_description Volume.set_name Volume.snapshot Volume.stat Volume.unset; do if ! test -L $$link; then ln -s volume.py $$link; fi; done
	cd $(DESTDIR)$(SCRIPTDIR)/volume/org.xen.xapi.storage.linstor; for link in Plugin.query Plugin.diagnostics Plugin.ls; do if ! test -L $$link; then ln -s plugin.py $$link; fi; done
	cd $(DESTDIR)$(SCRIPTDIR)/volume/org.xen.xapi.storage.linstor; for link in SR.probe SR.attach SR.create SR.destroy SR.detach SR.stat SR.ls; do if ! test -L $$link; then ln -s sr.py $$link; fi; done

release:
	tar --transform="s,^,$(PROJECT_NAME)-$(LATESTTAG)/," --owner=0 --group=0 -czf \
		$(PROJECT_NAME)-$(LATESTTAG).tar.gz $(SOURCES)

debrelease: release
