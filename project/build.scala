
import java.io.File
import java.lang.ProcessBuilder.Redirect

object BuildUtils {
  def join(root: File, folders: String*): File = {
    folders.foldLeft(root) { case (f, s) => new File(f, s) }
  }

  def join(folders: String*): File = {
    join(new File(folders.head), folders.tail: _*)
  }

  def isWindows: Boolean = {
    sys.props("os.name").toLowerCase.contains("windows")
  }

  def osPrefix: Seq[String] = {
    if (isWindows) {
      Seq("cmd", "/C")
    } else {
      Seq()
    }
  }

  def runCmd(cmd: Seq[String],
             wd: File = new File("."),
             envVars: Map[String, String] = Map()): Unit = {
    val pb = new ProcessBuilder()
      .directory(wd)
      .command(cmd: _*)
      .redirectError(Redirect.INHERIT)
      .redirectOutput(Redirect.INHERIT)
    val env = pb.environment()
    envVars.foreach(p => env.put(p._1, p._2))
    assert(pb.start().waitFor() == 0)
  }

  def uploadToBlob(source: String,
                   dest: String,
                   container: String,
                   accountName: String = "mmlspark"): Unit = {
    val command = Seq("az", "storage", "blob", "upload-batch",
      "--source", source,
      "--destination", container,
      "--destination-path", dest,
      "--account-name", accountName,
      "--account-key", Secrets.storageKey,
      "--overwrite", "true"
    )
    runCmd(osPrefix ++ command)
  }
}
