import sbtassembly.AssemblyKeys.assembly
import sbtassembly.AssemblyPlugin.autoImport.ShadeRule
import xerial.sbt.Sonatype._

import java.io.{File, PrintWriter}
import scala.xml.transform.{RewriteRule, RuleTransformer}
import scala.xml.{Node => XmlNode, NodeSeq => XmlNodeSeq, _}

name := "onnx-protobuf"
ThisBuild / organization := "com.microsoft.azure"
ThisBuild / scalaVersion := "2.12.15"

val scalaMajorVersion = 2.12

def pomPostFunc(node: XmlNode): scala.xml.Node = {
  new RuleTransformer(new RewriteRule {
    override def transform(node: XmlNode): XmlNodeSeq = node match {
      case e: Elem if e.label == "dependency"
        && e.child.exists(child => child.text == "org.scala-lang") =>
        Comment(s""" excluded scala dependency """.stripMargin)
      case e: Elem if e.label == "dependency"
        && e.child.exists(child => child.text == "com.google.protobuf") =>
        Comment(s""" excluded protobuf dependency since it is shaded """.stripMargin)
      case _ => node
    }
  }).transform(node).head
}

pomPostProcess := pomPostFunc

val settings = Seq(
  assembly / test := {},
  assembly / assemblyMergeStrategy := {
    case PathList("META-INF", xs@_*) => MergeStrategy.discard
    case x => MergeStrategy.first
  },
  assembly / assemblyOption := (assembly / assemblyOption).value.copy(includeScala = false),
  assembly / artifact := {
    val art = (assembly / artifact).value
    art.withClassifier(Some(""))
  },
  addArtifact(assembly / artifact, assembly)
)
ThisBuild / publishMavenStyle := true

lazy val root = (project in file("."))
  .settings(settings ++ Seq(
    libraryDependencies ++= Seq(
      "com.google.protobuf" % "protobuf-java" % "3.14.0"
    ),
    assembly / assemblyShadeRules ++= Seq(
      ShadeRule.rename("com.google.protobuf.**" -> "shade.com.google.protobuf.@1").inAll
    ),
    name := "onnx-protobuf",
  ): _*)

ThisBuild / sonatypeProjectHosting := Some(
  GitHubHosting("Microsoft", "onnx-protobuf", "mmlspark-support@microsoft.com"))
ThisBuild / homepage := Some(url("https://github.com/microsoft/onnx-protobuf"))
ThisBuild / scmInfo := Some(
  ScmInfo(
    url("https://github.com/microsoft/onnx-protobuf"),
    "scm:git@github.com:microsoft/onnx-protobuf.git"
  )
)
ThisBuild / developers := List(
  Developer("svotaw", "Scott Votaw",
    "synapseml-support@microsoft.com", url("https://github.com/svotaw")),
  Developer("mhamilton723", "Mark Hamilton",
    "synapseml-support@microsoft.com", url("https://github.com/mhamilton723"))
)

ThisBuild / licenses += ("MIT", url("https://github.com/microsoft/onnx-protobuf/LICENSE.md"))

ThisBuild / credentials += Credentials("Sonatype Nexus Repository Manager",
  "oss.sonatype.org",
  Secrets.nexusUsername,
  Secrets.nexusPassword)

pgpPassphrase := Some(Secrets.pgpPassword.toCharArray)
pgpSecretRing := {
  val temp = File.createTempFile("secret", ".asc")
  new PrintWriter(temp) {
    write(Secrets.pgpPrivate)
    close()
  }
  temp
}
pgpPublicRing := {
  val temp = File.createTempFile("public", ".asc")
  new PrintWriter(temp) {
    write(Secrets.pgpPublic)
    close()
  }
  temp
}
ThisBuild / publishTo := sonatypePublishToBundle.value

ThisBuild / dynverSonatypeSnapshots := true
ThisBuild / dynverSeparator := "-"
