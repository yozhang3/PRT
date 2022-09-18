package main

import(
  "fmt"
  "io"
  "io/ioutil"
  "os"
  "os/exec"
  "net/http"
  "log"
  "regexp"
  "time"
  "math/rand"
  "bufio"
)

func randomString(length int) string {
    rand.Seed(time.Now().UnixNano())
    b := make([]byte, length)
    rand.Read(b)
    return fmt.Sprintf("%x", b)[:length]
}

func main(){
  mux := http.NewServeMux()
	mux.HandleFunc("/", indexHandler)
  mux.HandleFunc("/favicon.ico", favicon)
	mux.HandleFunc("/upload", uploadFile)
  mux.HandleFunc("/chooseTime", chooseTime)
  mux.HandleFunc("/sipmsgs.html", sipHandler)
  mux.HandleFunc("/allmsgs.html", allHandler)
  mux.HandleFunc("/status.xml", statusHandler)
  mux.HandleFunc("/cfg.xml", cfgHandler)
  mux.HandleFunc("/net.cfg", netHandler)
  mux.HandleFunc("/tech.log", techHandler)
  mux.HandleFunc("/description.log", descriptionHandler)
  mux.HandleFunc("/background.jpeg", backgroundHandler)
  mux.HandleFunc("/cloud.png", cloudHandler)
  mux.HandleFunc("/tar.gz.png", tarHandler)


	if err := http.ListenAndServe(":9000", mux); err != nil {
		log.Fatal(err)
	}
}

func indexHandler(w http.ResponseWriter, r *http.Request) {
	// w.Header().Add("Content-Type", "text/html")
	// http.ServeFile(w, r, "index.html")
  content, _ := ioutil.ReadFile("index.html")
  w.Write(content)
}

func favicon(w http.ResponseWriter, r *http.Request) {
	// w.Header().Add("Content-Type", "text/html")
	// http.ServeFile(w, r, "index.html")
  content, _ := ioutil.ReadFile("favicon.ico")
  w.Write(content)
}

func backgroundHandler(w http.ResponseWriter, r *http.Request) {
	// w.Header().Add("Content-Type", "text/html")
	// http.ServeFile(w, r, "index.html")
  content, _ := ioutil.ReadFile("background.jpeg")
  w.Write(content)
}

func cloudHandler(w http.ResponseWriter, r *http.Request) {
  content, _ := ioutil.ReadFile("cloud.png")
  w.Write(content)
}

func tarHandler(w http.ResponseWriter, r *http.Request) {
  content, _ := ioutil.ReadFile("tar.gz.png")
  w.Write(content)
}

func uploadFile(w http.ResponseWriter, r *http.Request) {
    if r.Method != "POST" {
  		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
  		return
  	}

    // Parse our multipart form, 10 << 20 specifies a maximum
    // upload of 10 MB files.
    r.ParseMultipartForm(10 << 20)

    file, _, err := r.FormFile("myFile")
    if err != nil {
        fmt.Println("Error Retrieving the PRT File")
        fmt.Println(err)
        return
    }
    defer file.Close()
    // fmt.Printf("Uploaded PRT File: %+v\n", handler.Filename)
    // fmt.Printf("File Size: %+v\n", handler.Size)
    // fmt.Printf("MIME Header: %+v\n", handler.Header)


    buff := make([]byte, 512)
		_, err = file.Read(buff)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		filetype := http.DetectContentType(buff)
		if filetype != "application/x-gzip" {
			http.Error(w, "This is not a tar.gz file.", http.StatusBadRequest)
			return
		}

    // move the file pointer to the beginning so the io.Copy can copy every byte
		_, err = file.Seek(0, io.SeekStart)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

  	// Check if the file name starting with "prt"
    // prt_re, _ := regexp.Compile(`[pP][rR][tT].*`)
    // match := prt_re.MatchString(handler.Filename)
    // prt_n :=handler.Filename
    // if !match {
    //   prt_n ="prt"+handler.Filename
    // }

    prt_n :="prt-"+randomString(10)+".tar.gz"

  	// Create file
    dst, err := os.Create(prt_n)
  	defer dst.Close()
  	if err != nil {
  		http.Error(w, err.Error(), http.StatusInternalServerError)
  		return
  	}

  	// Copy the uploaded file to the created file on the filesystem
  	if _, err := io.Copy(dst, file); err != nil {
  		http.Error(w, err.Error(), http.StatusInternalServerError)
  		return
  	}

    // fmt.Fprintf(w, "Successfully Uploaded File\n")

    cmd := exec.Command("python3", "main_a.py", prt_n)
    stderr, _ := cmd.StderrPipe()
    cmd.Start()

    scanner := bufio.NewScanner(stderr)
    for scanner.Scan() {
        fmt.Println(scanner.Text())
    }
    if err := cmd.Wait(); err != nil {
      http.Error(w, "This is not a valid PRT file", http.StatusInternalServerError)
      return
  	}


    out, _ := cmd.CombinedOutput()
  	fmt.Printf("combined out:\n%s\n", string(out))

    prtn_re, _ := regexp.Compile(`(.*)\.tar\.gz`)
    prtn := prtn_re.FindStringSubmatch(prt_n)[1]

    content, _ := ioutil.ReadFile(prtn+"/chooseTime.html")
    w.Write(content)

}

func chooseTime(w http.ResponseWriter, r *http.Request) {
  if r.Method != "POST" {
    http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
    return
  }
  r.ParseMultipartForm(2)

  start_time := r.FormValue("start_time")
  // stop_time := r.FormValue("stop_time")
  prt_folder := r.FormValue("prt_folder")

  cmd := exec.Command("python3", "main_b.py", prt_folder, start_time)

  stderr, _ := cmd.StderrPipe()
  cmd.Start()
  // slurp, _ := io.ReadAll(stderr)
	// fmt.Printf("%s\n", slurp)
  scanner := bufio.NewScanner(stderr)
  for scanner.Scan() {
      fmt.Println(scanner.Text())
  }

  if err := cmd.Wait(); err != nil {
    http.Error(w, "This is not a valid PRT file", http.StatusInternalServerError)
    return
  }

  out, _ := cmd.CombinedOutput()
  fmt.Printf("combined out:\n%s\n", string(out))

  content, _ := ioutil.ReadFile(prt_folder+"/output.html")
  w.Write(content)
}

func sipHandler(w http.ResponseWriter, r *http.Request) {
  prt_folder := r.URL.Query().Get("prt_folder")
  content, _ := ioutil.ReadFile(prt_folder+"/sipmsgs.html")
  w.Write(content)
}

func allHandler(w http.ResponseWriter, r *http.Request) {
  prt_folder := r.URL.Query().Get("prt_folder")
  content, _ := ioutil.ReadFile(prt_folder+"/allmsgs.html")
  w.Write(content)
}

func statusHandler(w http.ResponseWriter, r *http.Request) {
  prt_folder := r.URL.Query().Get("prt_folder")
  w.Header().Set("Content-Type", "application/json; charset=utf-8")
  content, _ := ioutil.ReadFile(prt_folder+"/status.xml")
  w.Write(content)
}

func cfgHandler(w http.ResponseWriter, r *http.Request) {
  prt_folder := r.URL.Query().Get("prt_folder")
  w.Header().Set("Content-Type", "application/json; charset=utf-8")
  content, _ := ioutil.ReadFile(prt_folder+"/cfg.xml")
  w.Write(content)
}

func netHandler(w http.ResponseWriter, r *http.Request) {
  prt_folder := r.URL.Query().Get("prt_folder")
  content, _ := ioutil.ReadFile(prt_folder+"/net.cfg")
  w.Write(content)
}

func techHandler(w http.ResponseWriter, r *http.Request) {
  prt_folder := r.URL.Query().Get("prt_folder")
  content, _ := ioutil.ReadFile(prt_folder+"/tech.log")
  w.Write(content)
}

func descriptionHandler(w http.ResponseWriter, r *http.Request) {
  prt_folder := r.URL.Query().Get("prt_folder")
  content, _ := ioutil.ReadFile(prt_folder+"/description.log")
  w.Write(content)
}


// func sipHandler(w http.ResponseWriter, r *http.Request) {
//   if r.Method != "POST" {
//     http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
//     return
//   }
//   r.ParseMultipartForm(2)
// 	// http.ServeFile(w, r, "index.html")
//   prt_folder := r.FormValue("prt_folder")
//   content, _ := ioutil.ReadFile(prt_folder+"/sipmsgs.html")
//   w.Write(content)
// }
