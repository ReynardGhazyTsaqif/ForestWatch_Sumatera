# Prompt Template — Update Project Documentation ForestWatch Sumatera

Salin salah satu prompt di bawah sesuai situasi, lalu paste ke chat baru bersama file dokumentasi.

---

## PROMPT 1 — Update progress tahap tertentu (paling sering dipakai)

```
Saya sedang mengerjakan proyek ForestWatch Sumatera. 
Saya upload file dokumentasi proyek saya: [FORESTHWATCH_SUMATERA_DOCS.md]

Tolong perbarui dokumentasi tersebut dengan progress berikut:

TAHAP YANG SELESAI: [isi nomor dan nama tahap, contoh: Tahap 2 - Persiapan Data Spasial]

YANG SUDAH DIKERJAKAN:
- [isi poin-poin apa saja yang sudah dilakukan]
- [contoh: GeoJSON provinsi sudah diunduh dari GADM]
- [contoh: Nama wilayah sudah distandarisasi]

FILE YANG DIHASILKAN:
- [isi nama file dan lokasinya, contoh: province.geojson di data/geojson/]

KENDALA / CATATAN TEKNIS (jika ada):
- [isi masalah yang ditemukan dan cara mengatasinya]
- [ini penting agar tidak mengulang kesalahan yang sama]

TAHAP BERIKUTNYA YANG AKAN DIKERJAKAN: [isi nomor tahap berikutnya]

Perbarui tabel status tahap, bagian file penting, catatan teknis, 
dan tambahkan detail tahap berikutnya. Hasilkan ulang file .md yang sudah diperbarui.
```



## PROMPT 2 — Lanjut kerja sekaligus update docs

```
Saya sedang mengerjakan proyek ForestWatch Sumatera.
Saya upload file dokumentasi proyek: [FORESTHWATCH_SUMATERA_DOCS.md]

Baca dokumentasi tersebut, lalu bantu saya mengerjakan:
TAHAP BERIKUTNYA: [isi nomor dan nama tahap]

Konteks tambahan (jika ada):
- [isi informasi tambahan yang relevan]

Setelah selesai, perbarui juga file dokumentasinya dengan progress terbaru.
```

---

## PROMPT 3 — Ada masalah / error di tengah jalan

```
Saya sedang mengerjakan proyek ForestWatch Sumatera.
Saya upload file dokumentasi proyek: [FORESTHWATCH_SUMATERA_DOCS.md]

Saya sedang di TAHAP: [isi nomor dan nama tahap]
dan menemukan masalah berikut:

ERROR / MASALAH:
[paste error message atau deskripsi masalah di sini]

KODE / FILE YANG BERMASALAH:
[paste kode atau nama file jika relevan]

Tolong bantu selesaikan masalah ini. 
Jika ada perubahan penting pada pendekatan teknis, 
perbarui juga catatan teknis di dokumentasi.
```

---

## PROMPT 4 — Awal sesi baru tanpa progress baru (hanya orientasi)

```
Saya sedang mengerjakan proyek ForestWatch Sumatera.
Saya upload file dokumentasi proyek: [FORESTHWATCH_SUMATERA_DOCS.md]

Tolong baca dokumentasi tersebut dan berikan ringkasan:
1. Proyek ini tentang apa
2. Apa yang sudah selesai
3. Apa yang harus dikerjakan berikutnya dan langkah-langkahnya

Setelah itu saya akan mulai mengerjakan tahap berikutnya bersama kamu.
```

---

## Cara Pakai

1. Buka chat baru
2. Upload file `FORESTHWATCH_SUMATERA_DOCS.md`
3. Salin salah satu prompt di atas
4. Ganti bagian dalam `[kurung kotak]` dengan informasi Anda
5. Kirim

## Tips

- Selalu upload file `.md` terbaru di setiap sesi baru
- Setiap kali dokumentasi diperbarui, simpan versi barunya dan ganti file lama
- Sertakan error message lengkap jika ada bug, semakin detail semakin cepat diselesaikan
- Jika mengerjakan beberapa hal sekaligus, sebutkan semua di bagian "Yang Sudah Dikerjakan"
```