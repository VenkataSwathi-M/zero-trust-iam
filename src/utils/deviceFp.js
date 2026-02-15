export function getDeviceFp() {
  let fp = localStorage.getItem("device_fp");
  if (!fp) {
    fp = crypto.randomUUID();
    localStorage.setItem("device_fp", fp);
  }
  return fp;
}