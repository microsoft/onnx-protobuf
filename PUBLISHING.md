# Publishing

This scala project is setup to publish a Maven package to the Sonatype package store. The Sonatype Nexus username and pw are
looked up from SynapseML key vault at https://ms.portal.azure.com/#@microsoft.onmicrosoft.com/resource/subscriptions/e342c2c0-f844-4b18-9208-52c8c234c30e/resourceGroups/marhamil-mmlspark/providers/Microsoft.KeyVault/vaults/mmlspark-keys/overview
under the secrets nexus-us and nexus-pw.

## sbt
### Snapshot
- If you publish to a version that already exists, Sonatype will create a snapshot and publish it to the maven
repository https://oss.sonatype.org/content/repositories/snapshots/.
- Use the `sbt publishSigned` command to publish the snapshot version.

### Release
- We need Gpg to re-sign the jar file as saving the assembly jar as a regular jar breaks the file signature.
  - Please install Gpg and generate the key using the instructions documented [here](https://central.sonatype.org/publish/requirements/gpg/#installing-gnupg).
  - Credentials can be found in SynapseML key vault as documented above. `pgp-pw` from key-vault is the passphrase used in the gpg steps.
- To publish the release packages to Sonatype, first set the tag of the current commit to a version.
  - e.g., `git tag -a v0.9.3 -m "Initial checkin"`
- Login to az cli to fetch the credentials using the command: `az login`
- Sbt clean and compile the project: `sbt clean` and `sbt compile`
- Publish the package to the staging repository: `sbt publishSigned`
- Sign the onnx-protobuf jar using gpg
  - e.g., `gpg -ab onnx-protobuf\target\sonatype-staging\0.9.3\com\microsoft\azure\onnx-protobuf_2.12\0.9.3\onnx-protobuf_2.12-0.9.3.jar`
- Release the bundle to sonatype release and central repository: `sbt sonatypeBundleRelease` 
- Push the tag to git origin repo: `git push origin v0.9.3`
