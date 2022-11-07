# Publishing

This scala project is setup to publish a Maven package to the Sonatype package store. The Sonatype Nexus username and pw are
looked up from SynapseML key vault at https://ms.portal.azure.com/#@microsoft.onmicrosoft.com/resource/subscriptions/e342c2c0-f844-4b18-9208-52c8c234c30e/resourceGroups/marhamil-mmlspark/providers/Microsoft.KeyVault/vaults/mmlspark-keys/overview
under the secrets nexus-us and nexus-pw.

## sbt

To publish the packages to Sonatype, first set the tag of the current commit to a version.

e.g., git tag -a v0.9.0 -m "Initial checkin"

The run the following sbt commands:
publishSigned
sonatypeReleaseBundle (if public package)

Note that if you publish to a version that already exists, Sonatype will create a snapshot available at the maven
repository https://oss.sonatype.org/content/repositories/snapshots/
