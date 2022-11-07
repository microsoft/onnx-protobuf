import java.io.File
import BuildUtils.{join, uploadToBlob}
import sbt._
import Keys._

// The publishBlob task is used during testing to publish to a custom maven repository maintained by SynapseML.
// The repo is an Azure blob container at https://mmlspark.blob.core.windows.net/maven

//noinspection ScalaStyle
object BlobMavenPlugin extends AutoPlugin {
  override def trigger = allRequirements

  object autoImport {
    val publishBlob = TaskKey[Unit]("publishBlob", "publish the library to synapseml blob")
    val blobArtifactInfo = SettingKey[String]("blobArtifactInfo")
  }

  import autoImport._

  override def requires: Plugins = sbt.Plugins.empty

  override lazy val projectSettings: Seq[Setting[_]] = Seq(
    publishBlob := {
      publishM2.value
      val artifactName = s"${moduleName.value}_${scalaBinaryVersion.value}"
      val repositoryDir = new File(new URI(Resolver.mavenLocal.root))
      val orgDirs = organization.value.split(".".toCharArray.head)
      val localPackageFolder = join(repositoryDir, orgDirs ++ Seq(artifactName, version.value): _*).toString
      val blobMavenFolder = (orgDirs ++ Seq(artifactName, version.value)).mkString("/")
      uploadToBlob(localPackageFolder, blobMavenFolder, "maven")
      println(blobArtifactInfo.value)
    },
    blobArtifactInfo := {
      s"""
         |SynapseML OnnxMl Build and Release Information
         |---------------
         |
         |### Maven Coordinates
         | `${organization.value}:${moduleName.value}_${scalaBinaryVersion.value}:${version.value}`
         |
         |### Maven Resolver
         | `https://mmlspark.azureedge.net/maven`
         |""".stripMargin
    }
  )
}
