# ATO and compliance considerations

Every federal information system must be granted an Authority To Operate (ATO)
by an Authorizing Official in order to go into production.  A good in-depth
look can be found in [18F's before-you-ship docs](https://before-you-ship.18f.gov/ato/).  There
are currently a few options for getting an ATO:
* A [FedRAMP Tailored](https://tailored.fedramp.gov/) package.
* A full [FedRAMP JAB ATO](https://www.fedramp.gov/jab-authorization/).
* An agency ATO.  Every agency has their own process for issuing an ATO.
  An example of this is the GSA LATO (Lightweight ATO) process.

What ATO you get depends on what your project needs.  If you are doing this in
the GSA, you will probably want to follow the GSA LATO process, and most of the
compliance data that we have collected here is aimed at fulfilling that process.
That said, all of these ATO processes all map back to the NIST 800-53 controls,
so if you decide on a different ATO package, you ought to be able to use the
GSA LATO compliance data to help speed your ATO journey along.

*NOTE:*  This is an *example* here.  We are expecting
much of this documentation to be rewritten or significantly extended
by the vendor as they develop the TANF application and work with the HHS
ISSO and their particular ATO package.

## Compliance Masonry

We are using [Compliance Masonry](https://github.com/opencontrol/compliance-masonry) to
document all of the controls and how the different components satisfy them.  Every
component has a `compliance` directory which contains the documentation for that
component.  For example, the `upload` app has a
`Tanf-app/upload/compliance/component.yaml`
file, and the whole project has a `Tanf-app/compliance` directory
where everything is tied together with an `opencontrol.yaml` file, which
documents all of the components, the certifications (GSA LATO), and the
standards (NIST-800-63) that we use.  Components that do not have opencontrol
documentation are also documented in `Tanf-app/compliance/components`.

The idea is that *as you create code, you will also be creating and updating the
compliance documentation at the same time*.  You can run the `compliance-masonry diff LATO`
tool while in the `Tanf-app/compliance` directory to understand
what you still need to implement, find controls that are incomplete with
`compliance-masonry info -i partial`, etc.  Consult the 
[compliance-masonry usage docs](https://github.com/opencontrol/compliance-masonry/blob/main/docs/usage.md)
for more info.  

You can also use git tools to see what has changed between releases or
over time to see if changes are worthy of a Significant Change Request or
whatever.  For instance: `git checkout main ; git diff staging $(find . -name compliance -type d)`

Down the road, we would like to think that tools like this will evolve into
a Behaviour Driven Compliance Test suite that can actually test the implementation
of the controls described and let you know where you have gaps, but this is what
we have right now.

## Compliance Documentation

Every ATO package has a different set of documentation that it requires.  This
documentation changes over time, adding/removing controls or getting simpler or
more complex.  Most of the templates are in formats that we cannot emit or
edit in any reasonable way, so we have chosen to instead collect all the compliance
documentation you created with your code in a 
[GitBook](https://github.com/opencontrol/compliance-masonry/blob/master/docs/gitbook.md)
or a [PDF](https://github.com/opencontrol/compliance-masonry/blob/master/docs/gitbook.md#export-as-a-pdf)
that you can consult while filling out your ATO package.

## Generic ATO Process

This process is lightly modeled on the GSA LATO process, and is hopefully
similar enough to the HHS ATO process that it will be helpful in understanding
roughly what needs to be done, the roles that people will play,
and will generate documentation that will
be useful in filling out an SSP template for their agency.

To apply for a GSA LATO, you should:
1. Talk to your CISO or security team about where your ATO process is documented
   and what needs to be done to start the ATO process.  They may assign you an
   ISSO for you to talk with about this, who can help you get your ATO package
   and understand the procedure for real.
1. Read the 18F [Before You Ship](https://before-you-ship.18f.gov/ato/) document.
   It is probably much better at explaining what you should do in regular language.
   You will have to skip some of the 18F-specific processes,
   and instead use your own agency's ATO-related processes, but it should give you
   an idea of what things you will be doing.
1. Begin following the process outlined in the HHS ATO package or other documentation
   that your ISSO provides.
1. When selecting controls, you will select the controls specified in your
   ATO package or otherwise specified by your ISSO.
1. When documenting the controls, be aware that many controls have been stubbed
   out in the compliance directory, but you will probably need to add more
   detail, and probably more controls in general.  Wherever you see `XXX` in
   the documentation, you will definitely need to fill out details for the control.
1. Be sure to heavily leverage the P-ATOs on file with the FedRAMP program for cloud.gov,
   login.gov, and CircleCI.  They will probably take care of most of your controls,
   leaving you to document only your application and it's administration.

   This will require coordination with the ISSO, and cloud.gov has some
   [good documentation](https://cloud.gov/docs/compliance/ato-process/) on how
   that process works.
1. When you get to where you are filling out the [SSP](https://before-you-ship.18f.gov/ato/ssp/),
   you will want to generate the [compliance documentation](#compliance-documentation)
   from your project and use that information to help you understand what/how
   to fill out the different sections.

   A quick way to generate the [GitBook](https://github.com/opencontrol/compliance-masonry/blob/master/docs/gitbook.md)
   that lets you see the controls and other compliance information is:
   1. Make sure you have [Docker Desktop](https://www.docker.com/products/docker-desktop)
      installed.
   1. `cd Tanf-app && ./generate-compliance-gitbook.sh`
   1. open `Tanf-app/compliance/exports/pdf/tanf_compliance.pdf`
      in your favorite PDF viewer.

   Most of the sections in your SSP Template
   will have some text in the [GitBook](https://github.com/opencontrol/compliance-masonry/blob/master/docs/gitbook.md)
   that you can copy or use as a guide to fill out the various sections
   and controls, in addition to the more general guidance in the
   [SSP documentation](https://before-you-ship.18f.gov/ato/ssp/).
1. Continue executing the process outlined in your agency ATO package or other
   documentation from your ISSO until you have your ATO!

## Continuing Maintenance of the ATO

You may need to re-authorize your ATO if you make significant changes to
the system, especially if they change the security posture of the system.
You will also need to renew your ATO regularly according to a schedule
set by your ISSO.

These processes are also documented at a high level in the
18F [Before You Ship](https://before-you-ship.18f.gov/ato/) document.
