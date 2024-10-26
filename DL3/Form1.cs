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
                MessageBox.Show("��س�����ԧ�� YouTube");
                return;
            }

            string[] urls = videoUrls.Split(new[] { '\n', ',' }, StringSplitOptions.RemoveEmptyEntries); // �� URL �����������к�÷Ѵ����
            List<Task> downloadTasks = new List<Task>(); // ��ʵ�����Ѻ�� Task ��ô�ǹ���Ŵ

            foreach (var videoUrl in urls)
            {
                try
                {
                    var youtube = new YoutubeClient();
                    var video = await youtube.Videos.GetAsync(videoUrl.Trim()); // Trim ����ź��ͧ��ҧ
                    label1.Text = $"{video.Title}";

                    var streamManifest = await youtube.Videos.Streams.GetManifestAsync(video.Id);
                    var audioStreamInfo = streamManifest.GetAudioOnlyStreams().GetWithHighestBitrate();

                    if (audioStreamInfo != null)
                    {
                        // ����¹��鹷ҧ��������价�� Downloads
                        var downloadsPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Downloads");
                        var safeFileName = GetSafeFileName(video.Title) + ".mp3"; // ��ѧ��ѹ GetSafeFileName
                        var filePath = Path.Combine(downloadsPath, safeFileName); // �� downloadsPath

                        ProgressBar progressBar = new ProgressBar
                        {
                            Width = 600,
                            Height = 25,
                            Minimum = 0,
                            Maximum = 100,
                            Value = 0,
                            Location = new System.Drawing.Point(100,280 + (downloadTasks.Count * 30)) // ��èѴ���˹� ProgressBar
                        };
                        this.Controls.Add(progressBar);

                        downloadTasks.Add(DownloadAudioAsync(audioStreamInfo.Url, filePath, progressBar)); // ���� Task ŧ���ʵ�
                    }
                    else
                    {
                        MessageBox.Show($"��辺������§����Ѻ��ǹ���Ŵ: {video.Title}");
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"�Դ��ͼԴ��Ҵ㹡�ô�ǹ���Ŵ: {ex.Message}");
                }
            }

            await Task.WhenAll(downloadTasks); // ������ô�ǹ���Ŵ�������������

            MessageBox.Show("��ǹ���Ŵ��������������ó�!");
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
                        throw new Exception($"��ô�ǹ���Ŵ�������: {response.StatusCode}");
                    }

                    using (var stream = await response.Content.ReadAsStreamAsync())
                    using (var fileStream = new FileStream(filePath, FileMode.Create, FileAccess.Write, FileShare.None, 8192, true))
                    {
                        var buffer = new byte[524288]; // ��Ҵ buffer �� 512 KB
                        long totalBytesRead = 0;
                        long totalBytes = response.Content.Headers.ContentLength ?? 1;
                        int bytesRead;

                        while ((bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length)) > 0)
                        {
                            await fileStream.WriteAsync(buffer, 0, bytesRead);
                            totalBytesRead += bytesRead;

                            // �ѻവ ProgressBar �� UI thread
                            UpdateProgressBar(progressBar, totalBytesRead, totalBytes);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"�Դ��ͼԴ��Ҵ㹡�ô�ǹ���Ŵ: {ex.Message}");
            }
        }

        private void UpdateProgressBar(ProgressBar progressBar, long totalBytesRead, long totalBytes)
        {
            if (progressBar.InvokeRequired) // ��Ǩ�ͺ��ҵ�ͧ�ѻവ�� UI thread �������
            {
                progressBar.Invoke(new Action(() => UpdateProgressBar(progressBar, totalBytesRead, totalBytes)));
            }
            else
            {
                progressBar.Value = (int)((double)totalBytesRead / totalBytes * 100); // �ѻവ��� ProgressBar
                label2.Text = $"{progressBar.Value}%"; // �ѻവ�����繵�� Label
            }
        }

        private string GetSafeFileName(string fileName)
        {
            // ᷹����ѡ��з���������ö��㹪��������
            foreach (char c in Path.GetInvalidFileNameChars())
            {
                fileName = fileName.Replace(c, '_'); // �� '_' ᷹���
            }
            return fileName;
        }
    }
}
