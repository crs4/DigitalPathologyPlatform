---
layout: default
title: The Project
---

# The Promort Application

The goal of the ProMort Image Management System is to conduct a large scale epidemiological study of patients that have been diagnosed with a benign form of prostatic cancer but nevertheless died before expected.

The specific goal of the ProMort IMS is to create a collection of fully annotated images related to biopsies slides.

The system consists of two main parts: 

- the **ROIs annotation** phase, where users draw ROIs and take measures on the images;
- the **Clinical annotation** phase, where users perform the clinical review on each ROIs.
 
Users may belong to one or more of these possible groups: *First Reviewers*, *Second Reviewers* and *Third Reviewers* (Gold standards). As a *First Reviewer*, the user can perform both the **ROIs** and the **Clinical annotation** phases. *Second Reviewers* can perform only the **Clinical annotation** phase. The *Third Reviewer*, which come into play in case of discordance between the previous two reviewers, act as a Gold Standard doing the Clinical annotation phase his own.

The system keeps the anonymity of each case and the blindness between users through the application of a unique anonymised label to each review step different for each reviewer.  

# About this tutorial

This guide briefly explains the usage of the ProMort Application, that is quite the same for all the users. Any variations in the application behaviour for the different type of users are highlighted using a code color (<span style="color:red">First</span>,  <span style="color:blue">Second</span> and <span style="color:green">Third</span> Reviewer).