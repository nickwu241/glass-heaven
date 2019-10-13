# https://www.terraform.io/docs/providers/google/getting_started.html
provider "google" {
  credentials = "${file("gce-sa-secret.json")}"
  project     = "easy-companies-overview"
  region      = "us-east1"
}

resource "random_id" "instance_id" {
  byte_length = 8
}

# Need to enable Compute Engine API in the project.
resource "google_compute_instance" "default" {
  name         = "nickify-vm-${random_id.instance_id.hex}"
  machine_type = "n1-standard-2"
  zone         = "us-west1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-10"
    }
  }

  metadata_startup_script = "sudo apt-get update; sudo apt-get install -yq build-essential python-pip python3-distutils rsync; sudo pip install pipenv;"

  network_interface {
    network = "default"

    access_config {
      // Include this section to give the VM an external ip address
    }
  }

  metadata = {
    sshKeys = "nickwu:${file("~/.ssh/id_rsa.pub")}"
  }
}

resource "google_compute_firewall" "default" {
  name    = "app-firewall"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["3000"]
  }
}

output "ip" {
  value = "${google_compute_instance.default.network_interface.0.access_config.0.nat_ip}"
}
