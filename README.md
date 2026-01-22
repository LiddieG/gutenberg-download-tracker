# Gutenberg Download Tracker

## Overview
A collection of weekly top-downloaded Project Gutenberg books, enriched with structured metadata via an API, and the data stored as a growing time-series dataset for trend analysis.

## Project Goals

### Research Questions:

This tracker seeks to act as a form of research and analysis.
It will provide answers to some of these questions:

Which subjects dominate the weekly top 10 over time?
Do certain genres show seasonal patterns?
How stable are “popular” books week to week?
Which bookshelves repeatedly appear in rankings?
Is there a correlation between certain authors and seasonal patterns?

### Data Contract

A. Weekly ranking signal
week_date (ISO format)
rank (1–10)
book_id

B. Book metadata (from API)
title
authors
languages
subjects
bookshelves
download formats + URLs

## Data Sources

### Gutenberg weekly rankings page

Purpose: ranking signal only
Frequency: once per week
Output: list of top 10 book IDs

### Gutendex API

Purpose: metadata + download links
Access: REST JSON
One request per book ID

## Data Collected

## Project Structure

## Automation Plan

## Future Analysis Ideas


