##############
# parameters #
##############
# do you want to see the commands executed ?
DO_MKDBG:=0
# do you want dependency on the Makefile itself ?
DO_ALLDEP:=1
# do you want to check bash syntax?
DO_CHECK_SYNTAX:=1
# do you want to run mdl on md files?
DO_MD_MDL:=1
# do spell check on all?
DO_MD_ASPELL:=1
# do you want to check python syntax?
DO_SYNTAX:=1
# do you want to lint python files?
DO_LINT:=1
# do you want to lint python files using flake8?
DO_FLAKE8:=1
# do you want to lint python files using mypy?
DO_MYPY:=1

########
# code #
########
ALL:=

# silent stuff
ifeq ($(DO_MKDBG),1)
Q:=
# we are not silent in this branch
else # DO_MKDBG
Q:=@
#.SILENT:
endif # DO_MKDBG

ALL_SH:=$(shell find scripts -type f -and -name "*.sh")
ALL_STAMP:=$(addprefix out/, $(addsuffix .stamp, $(ALL_SH)))

MD_SRC:=$(shell find scripts -type f -and -name "*.md")
MD_BAS:=$(basename $(MD_SRC))
MD_MDL:=$(addprefix out/,$(addsuffix .mdl,$(MD_BAS)))
MD_ASPELL:=$(addprefix out/,$(addsuffix .aspell,$(MD_BAS)))

ALL_PY:=$(shell find scripts -type f -and -name "*.py")
ALL_SYNTAX:=$(addprefix out/,$(addsuffix .syntax, $(basename $(ALL_PY))))
ALL_LINT:=$(addprefix out/,$(addsuffix .lint, $(basename $(ALL_PY))))
ALL_FLAKE8:=$(addprefix out/,$(addsuffix .flake8, $(basename $(ALL_PY))))
ALL_MYPY:=$(addprefix out/,$(addsuffix .mypy, $(basename $(ALL_PY))))

ifeq ($(DO_CHECK_SYNTAX),1)
ALL+=$(ALL_STAMP)
endif # DO_CHECK_SYNTAX

ifeq ($(DO_MD_MDL),1)
ALL+=$(MD_MDL)
endif # DO_MD_MDL

ifeq ($(DO_MD_ASPELL),1)
ALL+=$(MD_ASPELL)
endif # DO_MD_ASPELL

ifeq ($(DO_SYNTAX),1)
ALL+=$(ALL_SYNTAX)
endif # DO_SYNTAX

ifeq ($(DO_LINT),1)
ALL+=$(ALL_LINT)
endif # DO_LINT

ifeq ($(DO_FLAKE8),1)
ALL+=$(ALL_FLAKE8)
endif # DO_FLAKE8

ifeq ($(DO_MYPY),1)
ALL+=$(ALL_MYPY)
endif # DO_MYPY

#########
# rules #
#########
.PHONY: all
all: $(ALL)
	@true

.PHONY: check
check:
	$(info doing [$@])
	$(Q)git grep "<<" src | grep -v "'COMMENT'" | grep -v "<<<" | grep -v multi_line_comment.bash || exit 0

.PHONY: debug
debug:
	$(info ALL_SH is $(ALL_SH))
	$(info ALL_STAMP is $(ALL_STAMP))
	$(info MD_SRC is $(MD_SRC))
	$(info MD_BAS is $(MD_BAS))
	$(info MD_ASPELL is $(MD_ASPELL))
	$(info MD_MDL is $(MD_MDL))
	$(info ALL_PY is $(ALL_PY))
	$(info ALL_SYNTAX is $(ALL_SYNTAX))
	$(info ALL_LINT is $(ALL_LINT))
	$(info ALL_FLAKE8 is $(ALL_FLAKE8))
	$(info ALL_MYPY is $(ALL_MYPY))

.PHONY: first_line_stats
first_line_stats:
	$(Q)head -1 -q $(ALL_SH) | sort | uniq -c

.PHONY: clean
clean:
	$(Q)rm -f $(ALL)

.PHONY: clean_hard
clean_hard:
	$(Q)git clean -qffxd

.PHONY: spell_many
spell_many:
	$(info doing [$@])
	$(Q)aspell_many.sh $(MD_SRC)

############
# patterns #
############
$(ALL_STAMP): out/%.stamp: % .shellcheckrc
	$(info doing [$@])
	$(Q)shellcheck --severity=error --shell=bash --external-sources --source-path="$$HOME" $<
	$(Q)pymakehelper touch_mkdir $@
$(MD_MDL): out/%.mdl: %.md .mdlrc .mdl.style.rb
	$(info doing [$@])
	$(Q)GEM_HOME=gems gems/bin/mdl $<
	$(Q)mkdir -p $(dir $@)
	$(Q)touch $@
$(MD_ASPELL): out/%.aspell: %.md .aspell.conf .aspell.en.prepl .aspell.en.pws
	$(info doing [$@])
	$(Q)aspell --conf-dir=. --conf=.aspell.conf list < $< | pymakehelper error_on_print sort -u
	$(Q)pymakehelper touch_mkdir $@
$(ALL_SYNTAX): out/%.syntax: %.py
	$(info doing [$@])
	$(Q)pycmdtools python_check_syntax $<
	$(Q)pymakehelper touch_mkdir $@
$(ALL_LINT): out/%.lint: %.py .pylintrc
	$(info doing [$@])
	$(Q)PYTHONPATH=python python -m pylint --reports=n --score=n $<
	$(Q)pymakehelper touch_mkdir $@
$(ALL_FLAKE8): out/%.flake8: %.py
	$(info doing [$@])
	$(Q)python -m flake8 $<
	$(Q)pymakehelper touch_mkdir $@
$(ALL_MYPY): out/%.mypy: %.py
	$(info doing [$@])
	$(Q)pymakehelper only_print_on_error mypy $<
	$(Q)pymakehelper touch_mkdir $@

##########
# alldep #
##########
ifeq ($(DO_ALLDEP),1)
.EXTRA_PREREQS+=$(foreach mk, ${MAKEFILE_LIST},$(abspath ${mk}))
endif # DO_ALLDEP
