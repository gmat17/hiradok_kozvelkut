# Analysis of the shift in the Hungarian public media after the 2026 election 🇭🇺
*Hungarian version below / Magyar verzió lentebb*

## 📌 About the Project
This project is a part of the thesis work of two courses in the Széchenyi István College for advanced studies. This README is really just a short insight, the main part of the analysis is available in the paper.

## Context
The public media was below a massive government control during Orban's goverments between 2010 and 2026. Its result was one of the strongest part of the FIDESZ propaganda. However, in 2026, Peter Magyar convinced Viktor Orban at the general elections, and he won with a two-third majority against the Fidesz, which resulted the end of Viktor Orban's system. And after the election many people noticed something strange with the public media: they functioned like a normal media without any fake news.

**The goal of this analysis is to show this shift using basic text minig methods.**

## ⚙️ Key Features
* **Hungarian NLP Pipeline:** Utilizes Stanford's `Stanza` for accurate lemmatization, Part-of-Speech (POS) tagging, and Named Entity Recognition (NER) specific to the Hungarian language.
* **Contextual Word Analysis:** Measures tone and sentiment shifts by analyzing the frequency of descriptive words (adjectives, verbs, nouns) in the immediate context of specific politicians (e.g., Viktor Orbán, Péter Magyar).
* **Entity Co-occurrence Networks:** Builds sliding-window (3-sentence) network graphs using `NetworkX` to visually map which actors and topics are grouped together in the media narrative before and after the election.

## 🛠️ Tech Stack
* **Language:** Python
* **Data Processing & NLP:** Pandas, Stanza
* **Network & Visualization:** NetworkX, Matplotlib, Seaborn

The codes were written with Gemini.
---

# A magyar közmédia változásának elemzése a 2026-os választások után 🇭🇺

## 📌 A projektről
Ez a projekt a Széchenyi István Szakkollégium két kurzusához készült beszámolójának része. Ez a README csupán egy rövid betekintést nyújt, az elemzés érdemi része magában a tanulmányban olvasható.

## Háttér
A közmédia erős kormányzati irányítás alatt állt az Orbán-kormányok idején 2010 és 2026 között, melynek eredményeként a Fidesz-propaganda egyik legerősebb eszközévé vált. 2026-ban azonban Magyar Péter legyőzte Orbán Viktort az országgyűlési választásokon, és kétharmados többséggel nyert a Fidesszel szemben, ami az Orbán-rendszer végét jelentette. A választások után sokan valami furcsára lettek figyelmesek a közmédiával kapcsolatban: úgy kezdett el működni, mint egy normális, álhírektől mentes médium.

**Ennek az elemzésnek a célja, hogy alapvető szövegbányászati módszerekkel mutassa be ezt a változást.**

## ⚙️ Főbb funkciók
* **Magyar NLP adatfeldolgozás:** A Stanford-féle `Stanza` könyvtárat használja a magyar nyelvre specifikus, pontos lemmatizáláshoz, szófaji (POS) címkézéshez és névelem-felismeréshez (NER).
* **Kontextuális szóelemzés:** A hangnem és a hangulat változásait méri a leíró szavak (melléknevek, igék, főnevek) gyakoriságának elemzésével megadott politikusok (pl. Orbán Viktor, Magyar Péter) közvetlen környezetében.
* **Együtt-említési hálózatok (Co-occurrence):** Csomópont-hálózatokat épít a `NetworkX` segítségével, 3 mondatos csúszóablak módszerrel, hogy vizuálisan feltérképezze, mely szereplők és témák jelennek meg egy csoportban a média narratívájában a választások előtt és után.

## 🛠️ Eszközök
* **Nyelv:** Python
* **Adatkezelés és NLP:** Pandas, Stanza
* **Hálózat és Vizualizáció:** NetworkX, Matplotlib, Seaborn

A kódok a Gemini segítségével készültek.