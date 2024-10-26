using System;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using System.Windows.Forms;
using YoutubeExplode;
using YoutubeExplode.Videos.Streams;
using System.Collections.Generic;

namespace DL3
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
            
        }

        private async void button1_Click(object sender, EventArgs e)
        {
            string videoUrls = textBox1.Text;
            if (string.IsNullOrWhiteSpace(videoUrls))
            {
                MessageBox.Show("กรุณาใส่ลิงก์ YouTube");
                return;
            }

            string[] urls = videoUrls.Split(new[] { '\n', ',' }, StringSplitOptions.RemoveEmptyEntries); // แบ่ง URL โดยใช้คอมม่าและบรรทัดใหม่
            List<Task> downloadTasks = new List<Task>(); // ลิสต์สำหรับเก็บ Task การดาวน์โหลด

            foreach (var videoUrl in urls)
            {
                try
                {
                    var youtube = new YoutubeClient();
                    var video = await youtube.Videos.GetAsync(videoUrl.Trim()); // Trim เพื่อลบช่องว่าง
                    label1.Text = $"{video.Title}";

                    var streamManifest = await youtube.Videos.Streams.GetManifestAsync(video.Id);
                    var audioStreamInfo = streamManifest.GetAudioOnlyStreams().GetWithHighestBitrate();

                    if (audioStreamInfo != null)
                    {
                        // เปลี่ยนเส้นทางที่เก็บไฟล์ไปที่ Downloads
                        var downloadsPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Downloads");
                        var safeFileName = GetSafeFileName(video.Title) + ".mp3"; // ใช้ฟังก์ชัน GetSafeFileName
                        var filePath = Path.Combine(downloadsPath, safeFileName); // ใช้ downloadsPath

                        ProgressBar progressBar = new ProgressBar
                        {
                            Width = 600,
                            Height = 25,
                            Minimum = 0,
                            Maximum = 100,
                            Value = 0,
                            Location = new System.Drawing.Point(100,280 + (downloadTasks.Count * 30)) // การจัดตำแหน่ง ProgressBar
                        };
                        this.Controls.Add(progressBar);

                        downloadTasks.Add(DownloadAudioAsync(audioStreamInfo.Url, filePath, progressBar)); // เพิ่ม Task ลงในลิสต์
                    }
                    else
                    {
                        MessageBox.Show($"ไม่พบไฟล์เสียงสำหรับดาวน์โหลด: {video.Title}");
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"เกิดข้อผิดพลาดในการดาวน์โหลด: {ex.Message}");
                }
            }

            await Task.WhenAll(downloadTasks); // รอให้การดาวน์โหลดทั้งหมดเสร็จสิ้น

            MessageBox.Show("ดาวน์โหลดทั้งหมดเสร็จสมบูรณ์!");
        }

        private async Task DownloadAudioAsync(string url, string filePath, ProgressBar progressBar)
        {
            try
            {
                using (var httpClient = new HttpClient())
                using (var response = await httpClient.GetAsync(url, HttpCompletionOption.ResponseHeadersRead))
                {
                    if (!response.IsSuccessStatusCode)
                    {
                        throw new Exception($"การดาวน์โหลดล้มเหลว: {response.StatusCode}");
                    }

                    using (var stream = await response.Content.ReadAsStreamAsync())
                    using (var fileStream = new FileStream(filePath, FileMode.Create, FileAccess.Write, FileShare.None, 8192, true))
                    {
                        var buffer = new byte[524288]; // ขนาด buffer เป็น 512 KB
                        long totalBytesRead = 0;
                        long totalBytes = response.Content.Headers.ContentLength ?? 1;
                        int bytesRead;

                        while ((bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length)) > 0)
                        {
                            await fileStream.WriteAsync(buffer, 0, bytesRead);
                            totalBytesRead += bytesRead;

                            // อัปเดต ProgressBar บน UI thread
                            UpdateProgressBar(progressBar, totalBytesRead, totalBytes);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"เกิดข้อผิดพลาดในการดาวน์โหลด: {ex.Message}");
            }
        }

        private void UpdateProgressBar(ProgressBar progressBar, long totalBytesRead, long totalBytes)
        {
            if (progressBar.InvokeRequired) // ตรวจสอบว่าต้องอัปเดตบน UI thread หรือไม่
            {
                progressBar.Invoke(new Action(() => UpdateProgressBar(progressBar, totalBytesRead, totalBytes)));
            }
            else
            {
                progressBar.Value = (int)((double)totalBytesRead / totalBytes * 100); // อัปเดตค่า ProgressBar
                label2.Text = $"{progressBar.Value}%"; // อัปเดตเปอร์เซ็นต์ใน Label
            }
        }

        private string GetSafeFileName(string fileName)
        {
            // แทนที่อักขระที่ไม่สามารถใช้ในชื่อไฟล์ได้
            foreach (char c in Path.GetInvalidFileNameChars())
            {
                fileName = fileName.Replace(c, '_'); // ใช้ '_' แทนที่
            }
            return fileName;
        }
    }
}
