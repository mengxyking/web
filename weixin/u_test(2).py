import os
import random
import string
import subprocess
import threading
import time
from time import sleep

import requests
from PIL import Image
from requests import RequestException
from datetime import datetime
from excel_handle import ThreadSafeExcelHandler
import uiautomator2 as u2

from myt.demo_py_x64.RapidOCR_json.api.python.demo1 import OCRProcessor
from myt.demo_py_x64.adb_test import run_adb_command
from myt.demo_py_x64.dama import dama_f
import adb1111
import re
import lxml.etree as etree

nick_name = ["Arno Elsie","Bartholomew Eipstein","Ryan Davy","Mavis Hoover","Antonia Garcia","Myron OCasey","Norman Horatio","Phil Owen","Neil Augustus","Douglas Irving","Zero Maltz","Cecil Walpole","Angela Bruce","Cedric Butler","Marcus Sapir","Vito Webster","Laura Joule","Odelette Emily","Irene Lowell","George Theresa","Barry Tom","Eunice Tours","Xenia Bertram","Boyd Anderson","Clare Evan","Daniel Aldridge","Tess Monroe","Carr Warner","Octavia Patience","Leif Eva","Omar Truman","Jeffrey Crichton","Merry Ingersoll","Denise Franklin","Lambert Locke","Mary Juliana","Viola Nichols","King Marner","York Needham","Laurel North","Asa Guy","Shirley Lindsay","Alan MacPherson","Angelo Tuttle","Donna Haywood","Lindsay Jennings","Kent Carrie","Lorraine Wilson","Enid Barton","Beacher Stowe","Armstrong Colclough","Joyce Titus","Bob Rockefeller","Conrad Huggins","Primo Howells","Pag Penn","Noah Partridge","Christine Thomas","Liz Emerson","Leo Bryan","Elaine Aly","Amy Berkeley","Tiffany David","Ruth Bennett","Ingrid Mike","Elliot Tennyson","Gerald Dutt","Hogan Bloomer","Felix Hume","Lester Felix","Trista Hicks","Maxine Fanny","Hazel Albert","Chloe Bertha","Tony Wordsworth","Sebastian Peggy","Samuel Abbott","Yehudi Polly","Bertha Marjory","Albert Pitman","Noel Barnard","Enoch Louisa","Joanne Philemon","Corey Coleridge","Joseph Jenkins","Elmer Strachey","Jason Eddie","Marsh Masefield","Bevis Winifred","Tina Lawson","Rock Camilla","Julian Wilde","Lawrence","Phyllis Nora","Ella Lily","Bart Johnson","Erica Christie","Veromca Mill","Kelly","Ives Blake","Gary Giles","Gloria Herty","Taylor Milne","Clark Dunbar","Randolph Senior","Bernard Vincent","Donahue Maugham","Sheila Burke","Truda Sailsbury","Cash Buckle","Christian Noel","Astrid Moses","Renata Lucas","Brian Swinburne","Colby ONeil","Page Wallace","Agnes Rebecca","Jane Lucy","Norton Frank","Adelaide Rhys","Louis Maud","Hugo Peter","Richard Zacharias","Kenneth Leighton","Sarah Longman","Don Browne","Juliet Bruno","Dominic Kingsley","Nydia Nixon","Ann Michael","Frank Brook","Gwendolyn Arthur","Moses Lincoln","Quinn Richardson","Larry Spender","Sally Cecillia","Griselda Springhall","Sam Reynolds","April Graham","Cathy Walton","Madge Wheeler","Gilbert Salome","Vincent Katrine","Letitia Hutt","Bard Pansy","Herbert Christy","Archibald Robbins","Abel Saxton","Zora Barrie","Miles Anne","Jacob Hardy","Merlin Bobby","Abraham Emmie","Suzanne Jordan","Mona Josh","Bishop Ruth","Agatha Whit","Rebecca Wagner","Meredith Delia","Valentine Lucius","Max Hosea","Antony Twain","Bradley Sophy","Harvey Murray","Belle Bridges","Burgess Bloor","Sara Peacock","Marshall Petty","Sandra Stevenson","Oswald Robeson","Paula Steinbeck","Vicky Burns","Hamiltion Timothy","Maurice Abe","Dick Kelsen","Una Lena","Donald Child","Hayden Pope","Jack Lloyd","Henry Morris","Edwiin Philip","Yvonne Yale","Sebastiane Agnes","Karen Rose","Natalie Habakkuk","Doris Windsor","Lydia Julius","Vanessa Walsh","Anna Bernal","Janice Quiller","Georgia Birrell","Roberta Stephen","Bill Gray","Ivy Catharine","Nigel Bert","Alston Gracie","Verna Cocker","Jerome Field","Sharon Wilhelmina","Natividad Adolph","Alexander Houston","Leona Croft","Miranda Joyce","Lena Hearst","Nelly Grantham","Pandora Oliver","Dora Belle","Olive Pearson","Betsy Luke","Robin Tommy","Peter Donne","Bella Gibbon","Julius Broad","Marlon Ernest","Tom Waters","Dana Wood","Penny Lamb","Prudence Benson","Chad Cotton","Mortimer Johnston","Morgan Cromwell","Walter Morley","Kim Sweet","Arlen Alsop","Theodore Stuart","Nelson Marcus","Jeremy Beaufort","Robert Tout","Andre Reade","Jill Jim","Elijah Lucia","Eartha Dupont","Jay Dierser","Renee Bartlett","Lilith Maurice","Ophelia Yonng","Bernice Gill","Kimberley Hudson","Mag Trollpoe","Godfery Lambert","Harold Victor","Norma Vaughan","Ethel Peg","Ted Raphael","Stanford Harvey","Clement Francis","Kitty Harrison","Andy Church","Rod Bart","Gail Hazlitt","Kerwin Scripps","Hugh","Upton Helina","Audrey","Joshua Rusk","Olivia Marcellus","Beatrice Clemens","Doreen Bessemer","Paddy Augustine","Justin","Charlotte Morton","Steward OConnor","Riva Aldington","Leonard Sherwood","Colbert Gregory","Dinah Marshall","Claude Ella","Herman Belloc","Jamie Carroll","Sabrina Bartholomew","Athena Lew","Barton Emma","Nicholas Clarke","Chester Bright","Pete Steele","Eugene MacDonald","Eleanore Gissing","Mark Zephaniah","Ira Edison","Jeff Ford","Valentina Mark","Griffith Southey","Tim Landon","Matthew Harry","Christ Samuel","Miriam Russell","Emmanuel Jones","Jerry Tobias","Hermosa Saul","Clarence Kelvin","Zara Madge","Grover Symons","Deirdre Morgan","Murphy Cooper","Byron Bertie","Augus Wright","Vera Betsy","Cornell Abraham","Hilary Eliot","Ursula Bray","Armand Margery","Vita Austin","Gill Occam","Sampson Alice","Debby Mackintosh","Rosalind Rob","Zoe Julian","Wanda Watt","Quentin Hobson","Bert Sharp","Elroy Horace","Belinda Kipling","Cara Alerander","Victor Douglas","Esther Bethune","Lynn Faulkner","Harriet Obadiah","Constance Toby","Boyce Rudolph","Darlene Saroyan","Quincy Becher","Maud Eugen","Patrick Walkley","Luther Funk","Hiram Haydn","Alberta Leonard","Annabelle Alcott","Page Matthew","Winni Nelly","Edmund Shakespeare","Selena Howard","Molly McCarthy","Gabrielle Bryce","Ula Poe","Edgar Hodge","Nora Dickens","Calvin Dorothy","Lauren Carl","Olga Harrod","Winfred Rutherford","Nathaniel Eden","Louise Doyle","Dominic Richards","Oliver Chaplin","Lillian Grote","Jonas Clarissa","Geraldine Browning","Ford Bach","Dale Doris","Raymond Carmen","Rudolf Sally","Beverly Susan","Joanna Doherty","Prima Evans","Ernest Powell","Bowen Bush","Dolores Cooke","Claire Dorothea","Dunn Gunter","Truman Cronin","Monroe Anthony","Harley Gardiner","Bertram Conan","Virgil Cowper","Gavin Snow","Poppy Christian","Jocelyn Joe","Gemma Maggie","Joyce Thompson","Newman Thodore","Gladys Yeates","Eudora DuBois","Ralap Scott","Xanthe Veblen","May DeQuincey","Walker Ezekiel","Carl Cumberland","Moore Crane","Hannah Valentine","Marvin Macadam","Gene Ruskin","Andrea Ferdinand","Ben Keats","Hubery Roosevelt","Linda Jimmy","Roderick Kennan","Diana Tony","Bridget Gilbert","Dylan Hugh","Kristin Humphry","Betty Dennis","Jim Milton","Ivan Wild","Ronald Godwin","Everley Armstrong","Ogden Martha","Ingemar Harold","Pamela Palmer","Darnell Blume","Tammy Gallacher","John Wilcox","Wordsworth Meredith","Spencer Copperfield","Theobald Chaucer","Nicole Foster","Frances Pulitzer","Phoenix Baker","Wallis Louis","Tracy Billy","Bblythe Jonson","Aubrey Benedict","Otto Sidney","Franklin Judith","Veronica Norris","Horace Hawthorne","Baird Cissie","Archer Edie","Sidney Stella","Teresa Juliet","Blanche Nicol","Jonathan Tyler","Burnell Sawyer","Adela Hamilton","Sigrid Coffey","Phoebe Mathilda","Barlow Ralph","Marian Wollaston","Eve Young","Maria Isaiah","Winifred Daniell","Regan Arabella","Hilary Patrick","Elva Tate","Earl Middleton","Xaviera Hemingway","Janet Louise","Berton Smith","Hobart Stephens","Polly Rossetti","Pearl Jean","Todd Caroline","Wade Dolly","Xavier Lattimore","Alice Nell","Yetta Carey","Uriah III","Gustave Warren","Maureen Carpenter","Mike Garden","Roxanne Beck","Leopold Laurie","Daphne Reed","Blithe Raleign","Joy Charlotte","Keith Walker","Ed Turner","Ellis Webb","Dawn Noyes","Jennifer Orlando","Kevin John","Tyrone Macaulay","Jesse Isabel","Isabel Spenser","Simon Euphemia","Regina Harte","Marcia Becky","Mandel Katharine","Amelia BurneJones","Stacey Lancelot","Magee Jackson","Anastasia Leigh","Porter Ben","Dana Zimmerman","Freda Maxwell","Cleveland Coverdale","Nina Ivan","Harry Pollitt","Morton Romeo","Caesar Elizabeth","Erin William","Derrick Geoffrey","Aaron Wolf","Frederica Margaret","Maxwell Lizzie","Delia Harrington","Philip Noah","Augustine Curme","Tobey Price","Queena Hopkins","Verne Alfred","Sabina Faraday","Alexia Bulwer","Jo Holt","June Keppel","Charles Daisy","Sandy Zechariah","Elizabeth Beerbohm","Melissa Haggai","Modesty Sheridan","Marjorie Crofts","Simona Brown","Fabian Taylor","Brook Isaac","Marico Back","Martina Harper","Wayne Vogt","Tiffany Nathaniei","Lou Adams","Isidore House","Frederic McDonald","Kay Thorndike","Iris Yerkes","Francis Pater","Duncan Jeremiah","Evangeline Malthus","Victoria Addison","Rita Mansfield","Jared Gaskell","Rae Nick","Ron Pepys","Spring Betty","Jo Gibson","Novia Boswell","Ward Frederick","Camille Pullan","Moira Charles","Wilbur Hobbes","Toby Eve","Hedy Malachi","Dave Fowler","Kerr Keynes","Egbert Dora","Quintion Montgomery","Helen Alick","Martha Babbitt","Giles Lynch","Elvira Moll","Odelia Bob","Chapman Daniel","Solomon Joshua","Chasel Hubbard","Candice Leopold","Alger Raglan","Ida Conrad","Barbara Jerry","Gustave Rosa","Barret Dalton","Gabriel Lee","Brady Hoyle","Bernie Chamberlain","Bess Roy","Burton Fast","Benjamin Darwin","Sandy Louie","Lisa Bellamy","Faithe Shaw","Cecilia Kellogg","Rosemary Huxley","Lucien Dobbin","Curitis George","Tracy Baldwin","Grace Simpson","Arlene IV","Drew Terry","Abigail Will","Matt Edith","Kyle Ulysses","Hunter Hansen","Ternence Carllyle","Susie Paul","Deborah Wodehous","Allen James","Dorothy","Webster Holmes","Greg Smollett","Ansel Edward","Thomas Ricardo","Antonio Collins","Murray Kathleen","Fay Jefferson","Rose Moore","Stephanie Fielding","Arthur Rhodes","Otis Raymond","Werner Norton","Clara Clare","Hulda Finn","Ferdinand Simon","Michaelia Connor","Barnett Gladstone","Ina Amelia","Stanley More","Christopher Edmund","Julia Jeremy","Vic Pritt","Fitch Kitto","Lyndon Gallup","Cynthia Jasper","Malcolm Acheson","Hyman Woolf","Payne Dewey","Michael","Brandon Sonmerfield","Gordon Johnny","Andrew Defoe","Kelly MacMillan","Elma Edgeworth","Michelle Wells","Rupert Congreve","Martin Bronte","Tyler Samson","Orville Yule","Celeste Forster","Judith Hart","Basil Tracy","Alva Joan","Elsie Jonah","Jacqueline Ann","Marina Richard","Len Ferguson","Tabitha Herbert","Carey Hughes","Alvin Sarah","Katherine Parker","Wright Rayleign","Evelyn Nahum","Broderick MacAdam","Colin Bacon","Heloise Ackerman","Irma Churchill","Bing Beard","Yvette Eisenhower","Gregary Wesley","Benedict Martin","Bruce Whyet","Blake Bauer","Zona Fred","Osborn Mac","Buck Bowen","Leila Freeman","Abner Hamlet","Mick Marion","Judy Violet","Ken Hope","Yves Anna","Rachel Gresham","Adonis Harriman","Eileen Dulles","Lucy Huntington","Elton Surrey","Owen Jacob","Vivian Service","Arvin Robinson","Megan Sinclair","Jessie Moulton","Yale Fox","Steven Benjamin","Sherry Zangwill","Reginald Wyatt","Channing Kent","Dwight Ellen","Alfred Grant","Booth Ward","Hardy Katte","Lennon Virginia","Alvis Jane","Willie Hewlett","Muriel Carnegie","Abbott Wilmott","Monica Bessie","Duke Charley","Lynn Temple","Zebulon Micah","Edith Spencer","Webb Duncan","Merle Lynd","Meroy Kitty","Ulysses Oscar","Yedda May","Guy Ramsden","Afra Hansom","Bennett Dryden","Cora Frances","Oscar Morse","Adam Bradley","Sophia","Darren Brooke","Aldrich Swift","Aries Buck","Levi Jerome","Mignon Effie","Blair Galsworthy","Amanda Christ","Emily Flower","Nat Clapham","Flora Jenny","Humphrey Bloomfield","Dean Robert","Gale Childe","Setlla Henley","Lance Raman","Hedda Longfellow","Crystal Rosalind","Glenn Constance","Salome Evelina","Michell Larkin","Avery Max","Beck Whitehead","Amos Boyle","Ruby Michelson","Marguerite Dodd","Cyril Roland","Myra Housman","Borg Piers","Aurora Robin","Coral Leacock","Eden Wat","Joan Geordie","Ingram Barney","Catherine Esther","Alva Eugene","Troy Halifax","Nancy Maria","Sean Kennedy","Haley Attlee","Sid Lewis","Howar Lindbergh","Clyde Bernard","Elsa Lytton","Roy Shelley","Beryl Thomson","Lee Cook","Ian Connie","Will Trevelyan","Lionel Bunyan","Parker Wylde","Daisy Dick","Cliff Gunther","Emma Roger","Mildred Bill","Atwood Kelly","Bruno Christiana","Cheryl Sophia","Wendy Newton","David Bentham","Jean Byron","Devin Bowman","Eden Andrew","Jessica Joseph","Myrna Stone","Woodrow Grace","Virginia Grey","Baron Craigie","Beau Julia","Mabel Commons","Julie Clement","Stan Dewar","Rory Sandy","Samantha Green","Les Johnson","Edward Henrietta","Susanna Gold","Ada I","Edwina Camp","Edison Washington","Alma Christopher","Scott Strong","Lewis Perkin","Winston Toynbee","Sylvia Job","Genevieve Jeames","Rachel Smedley","Theresa Adela","Dennis Priestley","Harlan Nehemiah","Mandy Antoinette","Madeline Bird","Adolph Clara","Warner Archibald","Benson Mond","Patricia Dillon","Darcy Morrison","Eric Toland","Rodney Jonathan","Nicola Law","Baldwin Chesterton","Zachary Tomlinson","Tab Sainsbury","Kirk Austen","Hale Pigou","Mamie Judd","Kama Mary","Lesley Jessie","Josephine Ted","Milo Motley","Fanny Gabriel","Honey Hal","Burke Dickey","Perry Nicholas","Isaac Hodgson","Penelope Lawrence","Venus Joel","Eli Nancy","Mirabelle Wycliffe","Sibyl London","Elvis Felton","Cornelius Newman","Wendell Nelson","Nathan Malan","Paul Marlowe","Rex Woolley","Berg Thoreau","Violet Brewster","Jodie Stilwell","Boris Eleanor","Saxon Ellis","Florence Jack","Quintina Chapman","Thera Van","Nick Hornby","Zenobia Walter","James Susanna","Maggie Aledk","Dempsey Bess","Carter Hill","Evan Hood","Reg Onions","Kennedy Pound","Montague Barrett","Adair Henry","Geoffrey Black","August Minnie","Valerie Sassoon","Hilda FitzGerald","Carol II","Vivien","Cornelia Wheatley","Susan Carter","Jenny Wallis","Bonnie Dan","William Sam","Caroline Gosse","Cherry Gus","Steward Nehemiah","Elsie Onions","Lennon Walker","Leona Dutt","Betsy BurneJones","Theodore Bert","Wanda Wilhelmina","Arno Nick","Esther Camp","Frances Carrie","Winfred Sainsbury","Grover Zechariah","Jonas Ellen","Oliver Nichols","Pag Lucius","Chad Wild","Clarence Ellis","Dennis Felix","Xanthe Micah","Newman Julian","Lambert Faraday","Ives Saxton","Xenia Law","Derrick Joe","Robert Bauer","Buck","Andrea Patience","Barton Cooke","Lynn Brewster","Tiffany Abbott","Nora Grote","Vera Salome","Olive Anne","Wallis Maggie","Roxanne Christ","Spencer Juliana","Gene Peter","Athena Eve","Fitch Roosevelt","Morgan Herbert","Humphrey Edmund","Jerome Cocker","Kelly Pater","Coral Addison","Luther Elsie","Susan Nahum","Wendell Waters","Burke Stilwell","Sabina Esther","Elton Trevelyan","Webster Ivan","Enid Walsh","Phil Bentham","Abner Cronin","Valentina Raymond","Jack Armstrong","Lisa Belle","Victor Barton","Valerie Malthus","Merry Field","Moore Parker","Cornelius Walpole","Phoenix Virginia","Upton Ezekiel","Dale Isaac","Geoffrey Oliver","Joy MacArthur","Gavin Evan","Oscar Dewey","Doris Bob","Bert Aledk","Olivia Carpenter","Bishop Wallace","Leopold Pearson","James Pope","Una Dodd","Lilith Austen","Raymond Yule","Reg Anna","Victoria Eleanor","Caesar Forster","Martin Milne","Kelly Robert","Richard Hamilton","May House","Page Ferdinand","Howar Bush","Zebulon OCasey","Amelia Curme","Gregary Edie","Jay Will","Katherine Dulles","Myron Malory","Brook Lowell","Vita Whyet","Clement Wyatt","Yves Bellamy","Edison Alsop","Adela Madge","Franklin Zangwill","Archer Stephens","Grace Lizzie","Catherine Eipstein","Jocelyn Aldridge","Betty Windsor","Wright Bruno","Elijah Johnston","Olga Dewar","Zachary Maud","Venus Bethune","Orville Mill","Arlen Gracie","Xaviera Hosea","Pete McDonald","Owen Goldsmith","Abraham Ernest","Janet Pritt","Albert Polly","Martha Cooper","Rachel Baker","Stephanie Newman","Oswald Jonah","Rock Oscar","Lionel Lamb","Cherry Raman","Dinah Alerander","Edith Harrington","Ben Jeremy","Nicholas Luke","Brandon Fred","Rupert Horatio","Madeline Kit","Mabel Philip","Egbert Maxwell","Caroline Bird","Rex Yerkes","Lyndon Halifax","Norton Gresham","Bruce Alice","Leila Chaplin","Salome Carmen","Michell Babbitt","Page Longman","Erin Haywood","Ursula Hearst","Andy Walter","Jeff Catharine","Len Toland","Eartha Hume","King Martha","Maud Gallup","Nydia Jerome","Blair Jack","Boyd Andrew","Truman Burns","Queena Kingsley","Penny Boyle","Gordon Bertha","Ophelia Pepys","Ted","Zenobia Cowper","Borg Lloyd","Bruno Becher","Benedict Bryan","Hubery Hamlet","Adelaide Hal","Virginia Smedley","Poppy Scott","Donna Becky","Osborn Lindsay","Michaelia Holt","Bridget Brooke","Sherry Housman","Tracy Rayleign","Jamie Clarke","Charles Grantham","Hugh Collins","Blake Norris","Bill Bertie","Hermosa Rebecca","Sarah Joshua","Brady Hoyle","Eve Coverdale","Sandy Snow","Bradley Toby","Edwina Powell","Jonathan Connie","Thomas Congreve","Winston Attlee","Ula Noel","Marshall Strachey","Ansel Lancelot","Toby Terry","Otto MacPherson","Susie Leopold","Sebastiane Pound","Constance Electra","Hale Surrey","Rudolf Van","Stacey Rutherford","Curitis Garden","Sibyl Harrison","Aurora Wood","Hamiltion Henry","Thera Rhodes","Noel Jordan","Judy Charlotte","Astrid Frank","Adam Mackintosh","Flora Strong","Taylor Butler","Christian Ruskin","Ingram Bessemer","Isidore Webster","Sigrid Nathaniei","Paddy Christiana","Evangeline Edison","Harry Emily","June MacAdam","Elvis Franklin","Daisy Jessie","Cara Gladstone","Aldrich Childe","Les Berkeley","Vanessa McCarthy","Rosemary William","Ellis Cook","Ruby Obadiah","Samuel Huntington","Natividad Hazlitt","Simon Wright","Tammy Tracy","Elva Louisa","Levi Antonia","Letitia Gregory","Giles Constance","Dick Eliot","Neil Sawyer","Irene Chamberlain","Roy Smollett","Tabitha Keppel","Martina","Stan Wilcox","Beck Needham","Nancy Webb","Kerwin Chapman","Drew Bernal","Winifred Daisy","Nina Boswell","Teresa Yonng","Edwiin Rusk","Ira Ford","Ford Kelvin","Rosalind Piers","Lynn Craigie","Magee Bridges","Penelope Laurie","Carol Dupont","Liz Sweet","Anna Hart","Gail Adolph","Roderick Brown","Vicky Victor","Christine Thodore","Kerr Noah","Miranda Horace","Abel Betsy","Rod Dunlop","Theobald Jefferson","Dylan Doherty","Chapman Emma","Zona Lily","Vic Louise","Dolores Huggins","Irma Judd","Ferdinand Maurice","Ryan Lytton","Ivan Margery","Brian Donne","Carter Geordie","Kim Bessie","Mandel Mac","Cash Jasper","Angela Galbraith","Glenn Crane","Will Warner","Fay Price","Clark Keynes","Donald Maria","Ralap Gus","Janice Fanny","Ron Henrietta","Winni Hopkins","Atwood Occam","John More","Eli Bacon","Arthur Irving","Justin Wordsworth","Bing Shakespeare","Alston Lee","Clyde Adam","Camille Clemens","Cathy Washington","Quentin Max","Zoe Bunyan","Riva Middleton","Afra Lattimore","Quintina Bowen","Modesty Back","Griselda Kelsen","Bart Tomlinson","Kevin Acheson","Mick Bowman","Ulysses Sailsbury","Hilary Paul","Abigail Roger","Jennifer Dickey","Sabrina Lena","Nathaniel Kitty","Elliot Nell","Crystal Hemingway","Nicola Alcott","Vincent Carl","Frederic Birrell","Louis Roy","Julian Jerry","Marsh Walton","Bob Steinbeck","Simona Wylde","Elroy MacMillan","Phyllis Beard","Godfery Martin","Harold Giles","Lorraine Masefield","Gill I","Sylvia Flynn","Maurice Fast","Parker Caroline","Celeste Trollpoe","Woodrow Louis","Madge Nancy","Webb Ward","Allen Lynch","Edmund Kennan","Cora Wheatley","Ward Adela","Josephine Arnold","Alva Tate","Theresa Mond","Tiffany Stella","Jeffrey Senior","Bartholomew Gunther","Ida Bloomer","Aubrey Barnard","Maria Agnes","Stanford","Adolph Silas","Sara Dennis","Horace Colclough","Hogan May","Avery Jenkins","Dave Carnegie","Lawrence Harrod","Boris Reed","Alice Finn","Cornelia Melville","Primo Jonson","Dempsey Cumberland","Cecilia Whitehead","Dawn Marion","Tab Foster","Lillian Cromwell","Frank Lewis","Clara Fox","Malcolm Harper","Kitty IV","Gary Hubbard","Sharon Sassoon","Colby Delia","Ronald Clare","Mildred Gill","Hiram Thomas","Sally Johnson","Perry Ralph","Regan Pullan","Yetta Eden","Debby Lincoln","Marico Lawson","Myrna Reynolds","Jane Mansfield","Hannah Partridge","Megan Arabella","Gerald Kellogg","Eleanore Poe","Lauren Holmes","Phoebe Wolf","Yedda Frederick","Kenneth London","Jeremy Commons","Evan Titus","Vivien Meg","Kent Jonathan","Gemma Saul","Kennedy Lambert","Antonio Wilson","Gustave Marcellus","Elsa Scripps","Kay Gissing","Milo Dickens","Rory Cecillia","Randolph","Tim Leighton","Miles Hugh","Deirdre Thompson","Melissa Jimmy","Alvis Dora","Natalie Gallacher","Gustave Sam","Hazel Peg","Troy Newton","Elizabeth Abraham","Erica Motley","Laurel Jennings","Abbott Howard","Lance Lawrence","Lou Rob","Emily Eugen","Ernest Hood","Jason Jane","Mirabelle Lindbergh","Octavia","Murray Bess","Yvette Ackerman","Jacob Archibald","Rose Sally","Joanne Grace","Arvin Malan","Ivy Charley","Gabrielle Albert","Barlow Humphry","Valentine Pullman","Bertha Grey","Walter Gibbon","Herbert Jacob","Eileen Rockefeller","Lester Fowler","Donahue Bradley","Darren Steele","Rachel Marshall","Jean Samuel","Marian Duncan","Annabelle Brook","Juliet Peacock","Miriam Mike","Cornell Sinclair","Beverly Zimmerman","Mike Hobbes","Gladys Jenny","Uriah Lyly","Nigel Harvey","George Clapham","Adonis Symons","Mary Isaiah","Cleveland Green","Archibald Julius","Pandora Edith","Ingrid Philemon","Don Gold","Tyrone Samson","Beau Bill","Dora Noyes","Michael Sander","Viola Chaucer","Alma Eveline","Bertram Graham","Greg Bray","Renata Clement","Mortimer Spenser","Mandy Huxley","Zora Betty","Heloise Hutt","Gabriel Yale","Benson Kitto","Colbert Sonmerfield","Wade Hope","Daniel Joel","Rae Anthony","Maxine Tout","Dunn Hornby","Dominic Nora","Merle Katharine","Eunice Bobby","Eric Susan","Kirk Nelson","Quintion Tours","Vivian Kent","Ingemar Pollitt","August Douglas","Violet Service","Lucien Blume","Matt Billy","Paul Vaughan","Yale Hewlett","Sampson Taylor","Burnell Dunbar","Harriet Bulwer","Wendy Margaret","Noah Godwin","Antony Joule","Veromca Hobson","Myra Maltz","Meredith Beerbohm","Kama Rossetti","Carey Hodge","Dominic Nixon","Lena Pitman","Lucy Winifred","Alan Stephen","Elma Watt","Pearl Meredith","Berton Doris","Hayden Haydn","Sidney Henley","Joshua Montgomery","Bevis Saroyan","Elvira Bartholomew","Chester Orlando","Vito Simon","Laura FitzGerald","Merlin Reade","Diana Gabriel","Murphy Russell","Agnes Maugham","Doreen Raleign","Ada Leacock","Andre Ramsden","Daphne Lucy","Paula Moulton","Keith Morse","Michelle Springhall","Harley Bell","Reginald Wagner","Aries Dan","Alexia Temple","Gwendolyn Ruth","Haley Abe","Joanna Warren","Hilda Funk","Ed Lynd","Matthew Rudolph","Shirley Adams","Quincy Black","Norma Southey","Emmanuel Johnny","Renee Rosa","Meroy Dierser","Tyler Sophy","Gilbert John","Virgil II","Yvonne Christy","Hugo Owen","Mamie Crofts","Jessica Dick","Mark Theresa","Dwight Landon","Bess Barney","Nelson Valentine","Marlon Dorothy","Claire Dillon","Dana Truman","Isaac Wheeler","Jo Stone","Porter Robinson","Sebastian Benson","Tony Hughes","Harlan Augustus","Nick Louie","Ann","Julius Barrie","Lee Thoreau","Eugene Conan","Jodie DeQuincey","Joyce Harte","Benjamin Amelia","Amos Timothy","Montague Coffey","William III","Marcia Guy","Angelo Adelaide","Trista Browne","Chloe Sarah","Conrad Violet","Philip Julia","Norman Matthew","Earl Stowe","Ina Thorndike","Pamela Carey","Sheila Nelly","Maggie Marjory","Darcy Emmie","Tess Wilmott","Alexander Euphemia","Warner Wells","Cliff Roland","Bernard Shelley","Geraldine Browning","Felix Robeson","Lydia Jackson","Suzanne Malachi","Emma Conrad","Agatha Tuttle","Armand Twain","Dorothy Tobias","Nelly Carter","Berg Michael","Alvin Veblen","Stanley Leigh","Jessie Gardiner","Larry Harriman","Robin Morley","Freda Spender","Ethel Toynbee","Everley Bart","Kyle Chesterton","Ogden Dorothea","Amy Sandy","Maxwell Richardson","Saxon Clara","Eden Bernard","Molly OConnor","Basil Elinor","Duncan Palmer","Elaine Cotton","Florence Camilla","Judith Alfred","Nathan Marner","Sam Johnson","Sid Swinburne","Henry Lucas","Booth Susanna","Augus Blake","Cedric Child","Alva Ted","Ken","Edgar Aly","Xavier Antoinette","Jim Woolf","Audrey Francis","Baird James","Rebecca Flower","Marjorie Evans","Sandy Jean","Payne Dobbin","Darnell Ferguson","Morton Dryden","Hilary Judith","Kimberley Christian","Truda Alick","Fanny Yeates","Fabian","Leo Nicol","Alberta Job","Andrew Judson","Peter Hoover","Candice Vincent","Hulda Tyler","Elmer Coleridge","Francis Galsworthy","Louise Ingersoll","Arlene DuBois","Joyce Hodgson","Scott Ulysses","Julie Bennett","Steven Hicks","Honey Hardy","Jesse Simpson","Spring Sapir","Rodney Ben","Frederica Tom","Broderick Gilbert","Leif Kelly","Jenny North","Sandra Patrick","Channing Freeman","Max Hudson","Hyman Gosse","Zara Elizabeth","Corey Hansen","Guy Bruce","Tina Stuart","Marvin Monroe","Bblythe Michelson","Marcus Eva","Cyril Stevenson","Veronica Grant","Helen Rose","Baldwin Mathilda","Werner Bloor","Ruth Finger","Alger Belloc","Bennett Jeremiah","Verna Rhys","Maureen Habakkuk","Belinda Mary","Darlene Raglan","Chasel Buckle","Joan Keats","Duke Effie","Otis Minnie","Tracy Katrine","Joseph Kennedy","Devin Whitman","Wordsworth Davy","Barret Lucia","Marina Sharp","Augustine Gray","Genevieve Morgan","Nicole Houston","Hedy Priestley","Harvey Katte","Asa Raphael","Christ Clarissa","Mag Morrison","Georgia Helina","York George","Prima Richards","Zero Morris","Bonnie Eddie","Wilbur Frances","Muriel Connor","Bernice Zacharias","Evelyn Moses","Patricia Turner","Bowen Christopher","Armstrong Willard","Amanda Pulitzer","Beacher Buck","Blithe Richard","Carr Tennyson","Byron Haggai","Cecil Gibson","Aaron Marcus","Tobey Woolley","Gale Josh","Enoch Sophia","Polly Gaskell","Cheryl Ella","Willie Walkley","Verne Daniell","Jacqueline Emerson","Omar Bach","Beryl Defoe","Mavis Benjamin","Sean Augustine","Julia Spencer","Belle Moll","Monroe Sidney","Marguerite Quiller","Mignon Edgeworth","Burton Leonard","Blanche Gunter","Samantha Benedict","Walker Herty","Wayne Wodehous","Burgess Beck","David Harold","Nat Bryce","Hardy Churchill","Kristin Doyle","Linda Vogt","Lindsay Anderson","Dean David","Isabel Barrett","Edward Arthur","Quinn Young","Karen Thackeray","Odelia Eugene","Beatrice Copperfield","Denise Evelina","Tom Bertram","Deborah Jim","Patrick Jeames","Mona Eisenhower","Sophia Daniel","Moira Wilde","Ella Pansy","Antonia Joan","Hunter Rosalind","Eudora Garcia","Iris Bartlett","Rita Bright","Claude Longfellow","Colin Beaufort","Clare Robin","Hobart Harry","Charlotte MacDonald","Susanna Sheridan","Roberta Lew","Anastasia Peggy","Novia Robbins","Bard Norton","April Milton","Alfred Felton","Barnett Broad","Boyce Penn","Jill Fielding","Selena Charles","Solomon Tommy","Carl Nicholas","Faithe Macadam","Lesley Church","Ternence Petty","Adair Dalton","Setlla Pigou","Cynthia Wesley","Ian Carroll","Moses Smith","Douglas Morton","Hedda Byron","Jared Bloomfield","Dana Isabel","Monica Darwin","Bernie Juliet","Herman Wat","Yehudi Wycliffe","Odelette Swift","Christopher Tony","Prudence Joseph","Regina Geoffrey","Gloria Murray","Calvin Whit","Delia Whittier","Bella Austin","Leonard Wollaston","Barry Hansom","Barbara Macaulay","Eden ONeil","Jo Howells","Todd Carllyle","Baron Croft","Jerry Kipling","Griffith Zephaniah","Lewis Joyce","Sylvia House","Hugh Davy","Belinda Tony","Olga Dryden","Mona Eliot","Elizabeth Ruskin","Tab Patience","Aldrich Parker","Dunn Pope","Grace Betty","Cora Rhys","Candice Carey","Clarence Gill","Flora Garden","Elaine Aldridge","Vita Juliet","Hilary Becky","Ralap Wolf","Tracy Dick","Burnell Becher","Pag Marjory","Norton Brooke","Hedy Locke","Alfred Norris","Veronica Fred","Archer Meredith","Brian Joshua","Eudora Barrie","Cornell Cooke","Tom Salome","Marvin Wallace","Truman Jeames","Nelly Yale","Barret Wylde","Ursula Raymond","Emmanuel Bruce","Denise Law","Hilary Truman","Jacob Sonmerfield","Magee Obadiah","Prudence Valentine","Marguerite Dierser","Marcia Evan","Ternence Nick","Judy Gregory","Simon Sherwood","Wendy Lee","Hayden Foster","Rose Agnes","Queena Julian","Webster Buckle","Blair Pansy","Toby Stevenson","Isaac Nahum","Caroline Toby","Gary Crofts","Tammy Sinclair","Cleveland Keynes","Irma Edison","Wade Toland","Gill Elsie","Mag Jean","Leo Russell","Beck Bloomer","Sherry Vincent","Kevin James","Tiffany Newton","Faithe Gibbon","Earl Eden","Sharon Dutt","Boris Wollaston","Spencer Lucius","Ophelia Charlotte","Maxine Larkin","Giles Blume","Benedict Eva","Jonathan Dolly","Peter Wagner","Phyllis Yeates","Wilbur Congreve","Susan Forster","Samantha Houston","Bevis Armstrong","Mike Motley","June Wodehous","Paddy Katharine","Buck Charley","Malcolm Eddie","Parker Nichols","Catherine Dewar","Marian Nelly","Sibyl","Sandy Julia","Humphrey Lindbergh","Morton Isaac","Leonard Eisenhower","Werner MacMillan","Curitis Bush","Theodore Tom","Celeste Longfellow","Regan Martin","Ingemar Windsor","Victor Felix","Nigel Turner","Susie Peter","Roderick Scripps","Stephanie Michael","Samuel Pepys","Melissa Poe","Andrew Mac","Egbert Rosa","Edmund MacAdam","Mabel Onions","Astrid Lucia","Dennis Antonia","Francis Melville","Bert Alice","Norman Middleton","Victoria Hill","Mary Gladstone","Herbert Jerry","Kitty Jenny","Harold Clapham","Frederic Pulitzer","Marlon Malan","Christ","Tabitha Arabella","Teresa II","Rodney Bach","Will Hazlitt","Conrad Harrison","Ruth Johnny","Mortimer Ackerman","Ansel Lamb","Lesley Bray","Simona Timothy","Baron Occam","Sean Malthus","Daniel North","Todd DeQuincey","Osborn Crane","Lilith Jeremiah","Ellis Coffey","Verne Rebecca","Arno Barrett","Hilda Rockefeller","Elvis Bauer","Zebulon Beard","Marcus Helina","Freda Harvey","Hyman Evans","Cecilia Lew","Nancy John","Dana Hume","Antony Conan","Vicky Horatio","Ted Fanny","Jerry Edgeworth","Darren Edie","Hardy Robinson","Muriel Hal","Katherine Jane","Griselda McDonald","Dwight Ezekiel","Chester Burke","Boyce Bessie","Marshall Bright","Angelo Tout","Lena Lily","Audrey Hugh","Bonnie Tate","Olive Bob","Arvin Maxwell","Frank Darwin","Amos Fast","Louis Lena","Sigrid Thomson","Natalie Johnson","George Dennis","April Field","Julie Perkin","Robin Belloc","Sebastian Habakkuk","Horace Chamberlain","Sandy Macadam","Benson Spender","Carl Jones","Penny Gibson","Lester Jasper","Sampson Ralph","Chad Whyet","Lawrence Maud","Tess ONeil","Dean Trollpoe","Lynn Augustus","Crystal Bryce","Zara Hemingway","Theobald Sailsbury","Cheryl Christopher","Ann Byron","Elma Susan","Rudolf Masefield","Jared May","Adolph Guy","Hazel Matthew","Arlene Bunyan","Eden Giles","King Crichton","Kerr Augustine","Burke Tracy","Ingram Carnegie","Henry Richard","Hulda Pritt","Jennifer Alerander","Eunice Marlowe","Elmer Sainsbury","Fay Sawyer","Lisa Mark","August Billy","Vanessa Joan","Tyler Madge","Dale Betsy","Merry Berkeley","Beryl Nathaniei","Rosemary Alfred","Miles Webb","Dominic Nixon","Erin Leopold","Moira George","Rachel Butler","Frederica Micah","Ruby DuBois","Norma Victor","Beacher Stephen","Isidore Jefferson","Ina Jonathan","Berg Geoffrey","Alvis Lytton","Lindsay Josh","Dawn Effie","Eugene Tomlinson","Len Nelson","Archibald Philemon","Betsy Hodgson","Claude Camilla","Ford Harrington","Fitch London","Mamie Kingsley","Phoebe Arnold","Maureen Shaw","Chasel Smith","Agatha Macaulay","Edgar Bill","Armand Sophy","Brandon Kelvin","Nina Pollitt","Viola Tyler","Omar Webster","Armstrong Burns","Myrna Ben","Boyd Joyce","Joseph Watt","Eve Austen","Stan Kelly","Hogan Mill","Aries Abe","Michelle Violet","Clement Malory","Mark Harry","Sheila Owen","Barry Richardson","Mirabelle Warner","Myra Pullan","Morgan Dalton","Berton Zephaniah","Baldwin Sam","Pearl Bulwer","Fanny Gunter","Bernie Patrick","Sabina Andrew","Aurora Graham","Carr Sander","Enoch Hicks","Lillian Grantham","Warner Frank","Noah Service","Lee Margaret","Rosalind Anne","Xenia Sally","Asa Tuttle","Ula Jack","Erica Noah","Kama Stephens","Helen Bridges","Bill","Thera Louie","Salome Adams","Alston Ivan","Harvey Bert","Thomas Dodd","Alva Nicol","Blithe Faraday","Dorothy","Lambert Faulkner","Hiram Paul","Oswald Holmes","Albert Ella","Charles Daniell","Geoffrey Geordie","Allen Leigh","Steven Mike","Anna Laurie","Jeremy Defoe","Daphne Hearst","Lucy Bernard","Nat Maltz","Kim Priestley","Avery Isaiah","Christian Whit","Kay Piers","Hermosa Bloomfield","Cyril Minnie","Maud Peggy","Solomon Montgomery","Ken Ted","Kent Beaufort","Richard Adolph","Atwood Galbraith","Adela Connor","Kelly Elinor","Ida Finger","Evelyn Rayleign","Barlow Bowen","Nathan Lindsay"]


def get_random_bounds_coord(element_info):
    """
    从元素的bounds中生成随机坐标（包含范围内所有可能坐标，不排除中心）

    参数:
        element_info (dict): 包含bounds信息的元素字典

    返回:
        tuple: (x, y) 随机坐标；若bounds无效则返回None
    """
    try:
        # 提取bounds的边界值
        bounds = element_info['bounds']
        left = bounds['left']
        right = bounds['right']
        top = bounds['top']
        bottom = bounds['bottom']
    except (KeyError, TypeError):
        print("错误：元素信息中bounds数据无效")
        return None

    # 检查坐标范围是否有效（left < right 且 top < bottom）
    if left >= right or top >= bottom:
        print("错误：bounds范围无效（left >= right 或 top >= bottom）")
        return None

    # 生成随机x坐标（范围：[left, right-1]，整数）
    x = random.randint(left, right - 1)
    # 生成随机y坐标（范围：[top, bottom-1]，整数）
    y = random.randint(top, bottom - 1)

    return (x, y)

def get_current_time_minute():
    """
    获取当前时间，精确到分钟
    返回格式：年-月-日 时:分（例如：2025-11-17 10:35）
    """
    current_time = datetime.now()
    # 格式化时间字符串，精确到分钟
    return current_time.strftime("%Y-%m-%d %H:%M")

def find_coords_by_text(d, target_text, exact_match=True):
    """
    根据文本内容查找控件，并返回其坐标信息
    :param d: uiautomator2 设备对象
    :param target_text: 目标文本（需匹配的控件text属性）
    :param exact_match: 是否精确匹配（True：完全相等；False：包含目标文本）
    :return: 坐标字典 {
        "x1": 左上角x, "y1": 左上角y,
        "x2": 右下角x, "y2": 右下角y,
        "center_x": 中心x, "center_y": 中心y
    }，未找到返回 None
    """
    # 获取当前界面的XML结构
    xml = d.dump_hierarchy()
    tree = etree.fromstring(xml.encode('utf-8'))

    # 遍历所有控件节点
    elements = tree.xpath('//node')
    for elem in elements:
        # 获取控件的text属性
        elem_text = elem.get('text', '').strip()
        print("elem_text=",elem_text)
        if not elem_text:
            continue  # 跳过无text的控件

        # 判断文本是否匹配（精确匹配或包含匹配）
        if (exact_match and elem_text == target_text) or (not exact_match and target_text in elem_text):
            # 解析控件的bounds坐标 [x1,y1][x2,y2]
            bounds_str = elem.get('bounds', '')
            coords = re.findall(r'\[(\d+),(\d+)]\[(\d+),(\d+)]', bounds_str)
            if not coords:
                continue  # 坐标解析失败则跳过

            # 提取坐标并转换为整数
            x1, y1, x2, y2 = map(int, coords[0])

            # 计算中心坐标
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            # 返回坐标信息字典
            # return {
            #     # "x1": x1,
            #     # "y1": y1,
            #     # "x2": x2,
            #     # "y2": y2,
            #     "center_x": center_x,
            #     "center_y": center_y
            # }
            return (center_x, center_y)

    # 未找到匹配的控件
    print(f"未找到text为「{target_text}」的控件")
    return None

def convert_to_black_white(self, input_path, output_path=None):
    """
    将彩色图片转换为黑白（灰度）图片

    参数:
        input_path: 输入图片的路径
        output_path: 输出图片的路径，默认为在原文件名后加"_bw"
    """
    try:
        # 打开图片
        with Image.open(input_path) as img:
            # 转换为灰度模式
            # L模式表示8位灰度图，每个像素用0-255表示亮度
            bw_img = img.convert('L')

            # 如果未指定输出路径，自动生成
            if not output_path:
                # 分离文件名和扩展名
                file_name, file_ext = os.path.splitext(input_path)
                output_path = f"{file_name}_bw{file_ext}"

            # 保存黑白图片
            bw_img.save(output_path)
            print(f"黑白图片已保存至: {output_path}")
            return output_path

    except Exception as e:
        print(f"转换失败: {str(e)}")
        return None


import os
import sys  # 需导入sys模块


def create_folder_on_current_disk():
    try:
        # 优先使用sys.argv[0]获取当前执行脚本的路径
        current_script_path = os.path.abspath(sys.argv[0])
    except IndexError:
        # 极端情况：若sys.argv[0]为空（极少发生），降级使用__file__
        if '__file__' in globals():
            current_script_path = os.path.abspath(__file__)
        else:
            raise RuntimeError("无法获取当前脚本路径，请检查执行环境")

    # 提取当前代码所在的磁盘（如 'C:\\' 或 'D:\\'）
    current_disk = os.path.splitdrive(current_script_path)[0] + os.sep
    # 拼接新建文件夹的路径
    folder_path = os.path.join(current_disk, "dy_temp")

    # 新建文件夹
    try:
        os.makedirs(folder_path, exist_ok=True)  # 增加exist_ok=True，避免重复创建报错
        print(f"已在 {current_disk} 上成功创建/使用文件夹：{folder_path}")
    except Exception as e:
        print(f"创建文件夹失败：{e}")
    return folder_path


def screenshot_by_coords(d, x1, y1, x2, y2, save_path=None):
    """
    根据坐标截取屏幕指定区域
    :param d: uiautomator2 设备对象
    :param x1: 左上角 x 坐标
    :param y1: 左上角 y 坐标
    :param x2: 右下角 x 坐标
    :param y2: 右下角 y 坐标
    :param save_path: 截图保存路径（如 "screenshot.png"，为 None 则不保存）
    :return: 裁剪后的 PIL 图像对象
    """
    SAVE_DIR = create_folder_on_current_disk()
    print(SAVE_DIR)
    # 生成带时间戳的文件名，避免重复
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    save_path = os.path.join(SAVE_DIR, f"screenshot_{timestamp}.png")
    # 获取全屏截图（返回 PIL.Image 对象）
    full_screenshot = d.screenshot()  # 等价于 d.screenshot(format='pillow')

    # 裁剪指定区域（crop 接收一个元组 (x1, y1, x2, y2)）
    # 注意：坐标需确保在屏幕范围内，否则会报错
    cropped_img = full_screenshot.crop((x1, y1, x2, y2))

    # 保存截图（如果指定了路径）
    if save_path:
        cropped_img.save(save_path)
    return save_path


def take_screenshot_white(d):
    try:
        SAVE_DIR = create_folder_on_current_disk()
        print(SAVE_DIR)
        # 生成带时间戳的文件名，避免重复
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(SAVE_DIR, f"screenshot_{timestamp}.png")
        # 截图并保存
        d.screenshot(save_path)
        print(f"截图已保存至：{save_path}")
        save_path_t = os.path.join(SAVE_DIR, f"screenshot_{timestamp}.png")
        convert_to_black_white(save_path, save_path_t)

        return save_path_t
    except BaseException as e:
        print("截图时，发生崩溃", str(e))
        return None

def generate_random_nickname():
    """
    生成随机昵称，由a-z、A-Z、0-9组成，长度为6-15个字符
    返回：随机昵称字符串
    """
    # 定义可选字符集：小写字母 + 大写字母 + 数字
    characters = string.ascii_letters + string.digits
    # 随机生成6-15之间的长度（包含6和15）
    length = random.randint(6, 15)
    # 从字符集中随机选择指定长度的字符，并拼接成字符串
    nickname = ''.join(random.choice(characters) for _ in range(length))
    return nickname

def backToWXHome(d):
    dd = 0
    time.sleep(2)
    while (dd < 10):
        #d.watcher("重新開始").when(text="重新開始").click()
        d.watcher.when("重新開始").click()
        if(d(text='重新開始').exists(timeout=1)):
            random_click_view(d,d(text='重新開始').info)
            time.sleep(2)

        elements = d(text='註冊')  # 获取所有文本为'some_text'的元素
        # print(len(elements))
        if (len(elements) > 0):
            return "1"
        time.sleep(0.5)
        d.press("back")
        time.sleep(0.5)


def send_get_request(url, params=None, headers=None, timeout=10):
    """
    发送 GET 请求的方法

    :param url: 请求的 URL 地址
    :param params: 字典类型的请求参数（会拼接到 URL 中）
    :param headers: 字典类型的请求头
    :param timeout: 超时时间（秒），默认 10 秒
    :return: 响应结果（字典类型，包含状态码和响应内容）
             失败时返回 None
    """
    try:
        # 发送 GET 请求
        response = requests.get(
            url=url,
            params=params,
            headers=headers,
            timeout=timeout
        )

        # 检查响应状态码（200 表示成功）
        response.raise_for_status()

        # 尝试解析 JSON 响应（如果响应是 JSON 格式）
        try:
            response_data = response.json()
        except ValueError:
            # 如果不是 JSON 格式，返回文本内容
            response_data = response.text

        return {
            "status_code": response.status_code,
            "data": response_data,
            "headers": dict(response.headers)  # 响应头
        }

    except RequestException as e:
        # 捕获所有请求相关异常（网络错误、超时等）
        print(f"GET 请求失败: {str(e)}")
        return None

def check_and_reconnect(d, device, element_len=30):
    """
    检查当前界面元素数量，与指定长度比较，决定是否重建设备连接
    :param d: 现有uiautomator2设备对象
    :param element_len: 参考元素数量阈值
    :param device: 设备标识（序列号或IP:端口）
    :return: 处理后的uiautomator2设备对象（可能是原对象或重建的对象）
    """
    try:
        # 获取当前界面XML结构
        xml = d.dump_hierarchy()
        # 解析XML并获取所有node元素（即UI控件）
        tree = etree.fromstring(xml.encode('utf-8'))
        elements = tree.xpath('//node')
        current_len = len(elements)
        print(f"当前界面元素数量: {current_len}, 阈值: {element_len}")

        # 比较元素数量
        if current_len > element_len:
            # 元素数量大于阈值，返回原设备对象
            print("元素数量符合要求，使用原设备连接")
            return d
        else:
            # 元素数量小于等于阈值，重建连接
            print(f"元素数量不足，尝试重建设备连接...")

            d.stop_uiautomator(wait=True)
            if ":" in device:  # 仅对IP:端口格式的无线设备执行disconnectd
                subprocess.run(f"adb disconnect {device}", shell=True, capture_output=True, text=True)
                print(f"已执行adb disconnect {device}，彻底断开无线ADB连接")

            # 停止当前uiautomator服务
            time.sleep(3)
            new_d = u2.connect(device)
            new_d.start_uiautomator()
            new_d.app_start(package_name="com.tencent.mm")
            print(f"设备 {device} 已重新连接")

            xml = d.dump_hierarchy()
            # 解析XML并获取所有node元素（即UI控件）
            tree = etree.fromstring(xml.encode('utf-8'))
            elements = tree.xpath('//node')
            current_len = len(elements)
            print(f"重连后: {current_len}, 阈值: {element_len}")

            return d

    except Exception as e:
        print(f"处理过程发生错误: {str(e)}，尝试重建连接...")
        # 发生异常时也尝试重建连接
        try:
            d.stop_uiautomator(wait=True)
        except:
            pass  # 忽略停止服务时的错误
        time.sleep(3)
        new_d = u2.connect(device)
        new_d.start_uiautomator()
        new_d.app_start(package_name="com.tencent.mm")

        return new_d

def random_click_view(d, view):
    bottom = view["bounds"]["top"]
    left = view["bounds"]["left"]

    random_x = int(left) + random.randint(2, 15)
    random_y = int(bottom) + random.randint(2, 15)
    print("开始点击")
    print(random_x, random_y)

    d.click(random_x, random_y)
def register(device,row1,ocr):
    d = u2.connect(device)
    print(d.dump_hierarchy())
    # adb_shell = f"adb -s {device} shell input tap {100} {300}"
    # d.shell(adb_shell)
    try:
        d.app_start(package_name="com.tencent.mm")
        backToWXHome(d)
        if (d(text="註冊").exists(timeout=3)):
            # d(text="关注").click()
            random_click_view(d, d(text="註冊").info)
            time.sleep(3)
        else:
            return "66"

        if (d(text="使用手機號碼註冊").exists(timeout=3)):
            # d(text="关注").click()
            random_click_view(d, d(text="使用手機號碼註冊").info)
            time.sleep(3)
        else:
            return "66"

        list_shuju, row_temp = row1
        if (d(text="請填寫暱稱").exists(timeout=35)):
            # d(text="关注").click()
            d(text="請填寫暱稱").set_text(generate_random_nickname())
        else:
            return "66"

        if (d(text="請填寫手機號碼").exists(timeout=3)):
            # d(text="关注").click()
            d(text="請填寫手機號碼").set_text(list_shuju[0])
        else:
            return "66"

        if (d(text="請設定密碼").exists(timeout=3)):
            # d(text="关注").click()
            d(text="請設定密碼").set_text("a"+str(list_shuju[0]))
        else:
            return "66"

        if (d(textContains="我已阅读").exists(timeout=3)):
            # d(text="关注").click()
            random_click_view(d, d(textContains="我已阅读").info)
            time.sleep(3)
        else:
            print("11")
            return "66"

        if (d(text="同意並繼續").exists(timeout=3)):
            # d(text="关注").click()
            print("meiyou 同意並繼續")
        else:
            d.press("back")
            time.sleep(2)


        if (d(text="同意並繼續").exists(timeout=3)):
            # d(text="关注").click()
            random_click_view(d, d(text="同意並繼續").info)
            time.sleep(10)
        else:
            return "66"

        # print(d.info)
        # print(d.dump_hierarchy())
        # path_temp = take_screenshot_white(d)
        # all_data = ocr.yewu(path_temp)
        # # alldata = ocr.getPoint_BY_PaddleOCRJson(path_temp, "我已")
        # # print(alldata)
        # # d.click(alldata[0], alldata[1])
        # if (str(all_data).count("我已") > 0):
        #     # d(text='添加评论...').click()
        #     print("我已")
        #     point = ocr.getPoint_by_data(all_data, "我已")
        #     if (len(point) > 0):
        #         d.click(point[0],point[1])
        #         time.sleep(3)
        # else:
        #     return "66"
        #
        # if (str(all_data).count("下一步") > 0):
        #     # d(text='添加评论...').click()
        #     print("下一步")
        #     point = ocr.getPoint_by_data(all_data, "下一步")
        #     if (len(point) > 0):
        #         d.click(point[0],point[1])
        #         time.sleep(3)
        # else:
        #     return "66"

        for i in range(5):
            d=check_and_reconnect(d,device)
            if (d(text="我已閱讀並同意私隱條款").exists(timeout=5)):
                # d(text="关注").click()
                print( )
                point_t = get_random_bounds_coord(d(text="我已閱讀並同意私隱條款").info)
                run_adb_command(device,point_t[0],point_t[1])
                time.sleep(5)
                break
            if (d(text="網頁無法使用").exists(timeout=1)):
                break
            if (d(text="無障礙方式").exists(timeout=1)):
                break

            path_temp = take_screenshot_white(d)
            all_data = ocr.yewu(path_temp)
            # alldata = ocr.getPoint_BY_PaddleOCRJson(path_temp, "我已")
            # print(alldata)
            # d.click(alldata[0], alldata[1])
            if (str(all_data).count("我已") > 0):
                # d(text='添加评论...').click()
                print("我已")
                point = ocr.getPoint_by_data(all_data, "我已")
                if (len(point) > 0):
                    d.click(point[0], point[1])
                    time.sleep(3)
                    time.sleep(3)
                    break

        else:

            print("meiyouquyanzheng")
            path_temp = take_screenshot_white(d)
            all_data = ocr.yewu(path_temp)
            # alldata = ocr.getPoint_BY_PaddleOCRJson(path_temp, "我已")
            # print(alldata)
            # d.click(alldata[0], alldata[1])
            if (str(all_data).count("我已") > 0):
                # d(text='添加评论...').click()
                print("我已")
                point = ocr.getPoint_by_data(all_data, "我已")
                if (len(point) > 0):
                    d.click(point[0], point[1])
                    time.sleep(3)
                    time.sleep(3)
            else:
                return "66"

        for i in range(5):
            d=check_and_reconnect(d,device)
            if (d(text="下一步").exists(timeout=5)):
                # d(text="关注").click()
                print("下一步")
                point_t = get_random_bounds_coord(d(text="下一步").info)
                run_adb_command(device,point_t[0],point_t[1])
                time.sleep(3)
                break
            if (d(text="網頁無法使用").exists(timeout=1)):
                break
            if (d(text="無障礙方式").exists(timeout=1)):
                break

            path_temp = take_screenshot_white(d)
            all_data = ocr.yewu(path_temp)
            # alldata = ocr.getPoint_BY_PaddleOCRJson(path_temp, "我已")
            # print(alldata)
            # d.click(alldata[0], alldata[1])
            if (str(all_data).count("下一步") > 0):
                # d(text='添加评论...').click()
                print("下一步")
                point = ocr.getPoint_by_data_true(all_data, "下一步")
                if (len(point) > 0):
                    d.click(point[0], point[1])
                    time.sleep(3)
                    break
        else:

            print("meiyou下一步")
            path_temp = take_screenshot_white(d)
            all_data = ocr.yewu(path_temp)
            # alldata = ocr.getPoint_BY_PaddleOCRJson(path_temp, "我已")
            # print(alldata)
            # d.click(alldata[0], alldata[1])
            if (str(all_data).count("下一步") > 0):
                # d(text='添加评论...').click()
                print("下一步")
                point = ocr.getPoint_by_data_true(all_data, "下一步")
                if (len(point) > 0):
                    d.click(point[0], point[1])
                    time.sleep(3)
            else:
                return "66"

        for i in range(5):
            d=check_and_reconnect(d,device)
            if (d(text="去驗證").exists(timeout=2)):
                # d(text="关注").click()
                print("quyanzheng")
                point_t = get_random_bounds_coord(d(text="去驗證").info)
                run_adb_command(device,point_t[0],point_t[1])
                time.sleep(1)
                run_adb_command(device, point_t[0], point_t[1])
                time.sleep(5)
                # temp_t = d(text="去驗證").info
                # random_click_view(d, temp_t)
                # time.sleep(1)
                # random_click_view(d, temp_t)
                # time.sleep(8)
                # d.stop_uiautomator(wait=True)
                # time.sleep(1)
                # d = u2.connect(device)
                break
            if (d(text="網頁無法使用").exists(timeout=1)):
                break
            if (d(text="無障礙方式").exists(timeout=1)):
                break

            path_temp = take_screenshot_white(d)
            all_data = ocr.yewu(path_temp)
            # alldata = ocr.getPoint_BY_PaddleOCRJson(path_temp, "我已")
            # print(alldata)
            # d.click(alldata[0], alldata[1])
            if (str(all_data).count("去") > 0):
                # d(text='添加评论...').click()
                print("去")
                point = ocr.getPoint_by_data(all_data, "去")
                if (len(point) > 0):
                    d.click(point[0], point[1])
                    time.sleep(3)
                    time.sleep(15)
                    break
        else:
            print("meiyouquyanzheng")
            path_temp = take_screenshot_white(d)
            all_data = ocr.yewu(path_temp)
            # alldata = ocr.getPoint_BY_PaddleOCRJson(path_temp, "我已")
            # print(alldata)
            # d.click(alldata[0], alldata[1])
            if (str(all_data).count("去") > 0):
                # d(text='添加评论...').click()
                print("去")
                point = ocr.getPoint_by_data(all_data, "去")
                if (len(point) > 0):
                    d.click(point[0], point[1])
                    time.sleep(3)
                    time.sleep(15)
            else:
                return "66"

        # path_temp = take_screenshot_white(d)
        # all_data = ocr.yewu(path_temp)
        # if (str(all_data).count("去") > 0):
        #     # d(text='添加评论...').click()
        #     print("去")
        #     point = ocr.getPoint_by_data(all_data, "去")
        #     if (len(point) > 0):
        #         d.click(point[0],point[1])
        #         time.sleep(8)
        # else:
        #     return "66"
        time.sleep(1)
        d=check_and_reconnect(d,device)
        if (d(text="網頁無法使用").exists(timeout=3)):
            # d(text="关注").click()
            # random_click_view(d, d(text="去驗證").info)
            # time.sleep(8)
            return "100"
        return "1"


        #result_temp = ThreadSafeExcelHandler.update_cell_by_row_col(row_temp,4,"完成")
        # print(result_temp)
    except Exception as e:
        print(e)
        return "66"

def jiaoyanma(device):
    d = u2.connect(device)

    for i in range(5):
        d=check_and_reconnect(d, device)
        if (d(textContains = "無障礙方式").exists(timeout=5)):
            # d(text='添加评论...').click()
            print("無障礙方式")
            time.sleep(3)
            # random_click_view(d,d(textContains = "無障礙方式").info)
            point_t = get_random_bounds_coord(d(textContains = "無障礙方式").info)
            run_adb_command(device, 100, point_t[1])
            time.sleep(1)
            #run_adb_command(device, point_t[0], point_t[1])
            time.sleep(3)
            break
        else:
            print("没有無障礙方式")
            time.sleep(3)
        path_temp = take_screenshot_white(d)
        all_data = ocr.yewu(path_temp)
        # alldata = ocr.getPoint_BY_PaddleOCRJson(path_temp, "我已")
        # print(alldata)
        # d.click(alldata[0], alldata[1])
        if (str(all_data).count("方式") > 0):
            # d(text='添加评论...').click()
            print("方式o")
            point = ocr.getPoint_by_data(all_data, "方式")
            if (len(point) > 0):
                d.click(point[0], point[1])
                time.sleep(3)
                break
    else:

        print("meiyou 无障碍方式，重新尝试")
        path_temp = take_screenshot_white(d)
        all_data = ocr.yewu(path_temp)
        # alldata = ocr.getPoint_BY_PaddleOCRJson(path_temp, "我已")
        # print(alldata)
        # d.click(alldata[0], alldata[1])
        if (str(all_data).count("方式") > 0):
            # d(text='添加评论...').click()
            print("方式o")
            point = ocr.getPoint_by_data(all_data, "方式")
            if (len(point) > 0):
                d.click(point[0], point[1])
                time.sleep(3)
        else:
            return "66"
    return "1"
    # d.stop_uiautomator(wait=True)
    # time.sleep(3)
    # d = u2.connect(device)#最近半年沒有被封鎖賬號
    #
    # if (d(textContains="最近半年沒有被封鎖賬號").exists(timeout=15)):
    #     # d(text='添加评论...').click()
    #     print("最近半年沒有被封鎖賬號")
    #
    #     return "66"
    # else:
    #     print("验证成功")
    #     d.stop_uiautomator(wait=True)
    #     return "1"

    # path_temp = take_screenshot_white(d)
    # all_data = ocr.yewu(path_temp)
    # if (str(all_data).count("完成") > 0 and str(all_data).count("半年") > 0):
    #     return "88"  # 备注其他状态
    # else:
    #     print("验证成功")
    #     d.stop_uiautomator(wait=True)
    #     return "1"
        # time.sleep(3)

    # for i in range(10):
    #     time.sleep(3)
    #     if (find_coords_by_text(d,"依次點擊：")):
    #         print("刷新驗證")
    #         time.sleep(3)
    #         break
    #     else:
    #         print("me刷新驗證")
    # else:
    #     return "66"

    # for i in range(5):
    #     path_t = screenshot_by_coords(d, 14, 320, 720, 1054)
    #     response_text = dama_f(path_t)
    #     print(response_text)
    #     if (response_text is not None):
    #         points = response_text["data"]["data"]
    #         print(points)
    #         point_list = str(points).split("|")
    #
    #         for point in point_list:
    #             print(point)
    #             point_small = str(point).split(",")
    #             if (len(point_small) > 1):
    #                 d.click(int(point_small[0]) + 14, int(point_small[1]) + 320)
    #                 time.sleep(1)
    #         else:
    #             # return "66"
    #             print("11")
    #
    #         if (find_coords_by_text(d,"確定")):#確定
    #             # d(text="关注").click()
    #             #random_click_view(d, d(text="確定").info)
    #             point_t = find_coords_by_text(d,"確定")
    #             d.click(point_t[0],point_t[1])
    #             time.sleep(8)
    #         else:
    #             return "66"

            # path_temp = take_screenshot_white(d)
            # all_data = ocr.yewu(path_temp)
            # if (str(all_data).count("定") > 0):#点击确定按钮
            #     # d(text='添加评论...').click()
            #     print("点击确定按钮")
            #     point = ocr.getPoint_by_data(all_data, "定")
            #     if (len(point) > 0):
            #         d.click(point[0], point[1])
            #         time.sleep(15)
            # else:
            #     print("meiyou 确定按钮")
            #     return "66"
            #     #time.sleep(3)


def check_bank_cark(device,visa_ThreadSafeExcelHandler,ThreadSafeExcelHandler,list_shuju,row_temp,result_t):

    list_t, row_t = result_t
    visa_ThreadSafeExcelHandler.update_cell_by_row_col(row_t, 5, "执行中")


    d = u2.connect(device)
    for i in range(10):
        d=check_and_reconnect(d,device)
        if (d(text="驗證銀行卡").exists(timeout=6)):
            point_t = get_random_bounds_coord(d(text="驗證銀行卡").info)
            run_adb_command(device, point_t[0], point_t[1])
            time.sleep(1)
            run_adb_command(device, point_t[0], point_t[1])
            #time.sleep(5)
            # d(text='驗證銀行卡').click()
            # print("驗證銀行卡")
            # time.sleep(25)
            # d.stop_uiautomator(wait=True)
            # time.sleep(1)
            # d = u2.connect(device)
            break
        elif (d(textContains="最近半年沒有被封鎖賬號").exists(timeout=15)):
            print("最近半年沒有被封鎖賬號")
            ThreadSafeExcelHandler.update_cell_by_row_col(row_temp, 4, get_current_time_minute())
            ThreadSafeExcelHandler.update_cell_by_row_col(row_temp, 5, "二维码")

            return "101"
        if (d(text="驗證卡").exists(timeout=3)):
            break

        path_temp = take_screenshot_white(d)
        all_data = ocr.yewu(path_temp)
        # alldata = ocr.getPoint_BY_PaddleOCRJson(path_temp, "我已")
        # print(alldata)
        # d.click(alldata[0], alldata[1])
        if (str(all_data).count("行卡") > 0):
            # d(text='添加评论...').click()
            print("行卡")
            point = ocr.getPoint_by_data(all_data, "行卡")
            if (len(point) > 0):
                d.click(point[0], point[1])
                time.sleep(3)
                time.sleep(15)
                break
    else:
        print("没有驗證銀行卡")
        # return "66"
        path_temp = take_screenshot_white(d)
        all_data = ocr.yewu(path_temp)
        # alldata = ocr.getPoint_BY_PaddleOCRJson(path_temp, "我已")
        # print(alldata)
        # d.click(alldata[0], alldata[1])
        if (str(all_data).count("行卡") > 0):
            # d(text='添加评论...').click()
            print("行卡")
            point = ocr.getPoint_by_data(all_data, "行卡")
            if (len(point) > 0):
                d.click(point[0], point[1])
                time.sleep(3)
                time.sleep(15)
        elif (str(all_data).count("半年") > 0):
            print("最近半年沒有被封鎖賬號")
            ThreadSafeExcelHandler.update_cell_by_row_col(row_temp, 4, get_current_time_minute())
            ThreadSafeExcelHandler.update_cell_by_row_col(row_temp, 5, "二维码")
            return "101"

    # d.stop_uiautomator(wait=True)
    # time.sleep(3)
    # d = u2.connect(device)

    for i in range(30):
        d=check_and_reconnect(d,device)
        if (d(text="驗證卡").exists(timeout=3)):
            break
        else:
            print("没有驗證卡")
    else:
        return "66"

    d.swipe(200,800,200,100)
    time.sleep(1)
    d.swipe(200, 800, 200, 100)
    time.sleep(8)
    editTexts = d(className="android.widget.EditText")
    print(len(editTexts))

    if(len(editTexts) != 4):
        return "66"

    for i in range(len(editTexts)):
        if(i == 0 ):
            editTexts[i].set_text(list_t[i])
            time.sleep(1)
        if (i == 1):
            editTexts[i].set_text(random.choice(nick_name))
            time.sleep(1)
        if (i == 2):
            editTexts[i].set_text(list_t[i])
            time.sleep(1)
        if (i == 3):
            editTexts[i].set_text(list_t[1])
            time.sleep(1)
    time.sleep(8)
    for i in range(15):
        d=check_and_reconnect(d,device)
        if (d(textContains="下一步").exists(timeout=3)):
            # d(text="关注").click()
            # temp_t = d(textContains="下一步").info
            # random_click_view(d, temp_t)
            # time.sleep(1)
            # random_click_view(d, temp_t)
            # time.sleep(2)
            # d.stop_uiautomator(wait=True)
            # time.sleep(1)
            # d = u2.connect(device)
            point_t = get_random_bounds_coord(d(text="下一步").info)
            run_adb_command(device, point_t[0], point_t[1])
            time.sleep(1)
            run_adb_command(device, point_t[0], point_t[1])
            break

        if (d(textContains="繼續註冊").exists(timeout=1)):
            break

        path_temp = take_screenshot_white(d)
        all_data = ocr.yewu(path_temp)
        # alldata = ocr.getPoint_BY_PaddleOCRJson(path_temp, "我已")
        # print(alldata)
        # d.click(alldata[0], alldata[1])
        if (str(all_data).count("下一步") > 0):
            # d(text='添加评论...').click()
            print("去")
            point = ocr.getPoint_by_data(all_data, "下一步")
            if (len(point) > 0):
                d.click(point[0], point[1])
                time.sleep(3)
                break
    else:
        print("没有下一步")
        path_temp = take_screenshot_white(d)
        all_data = ocr.yewu(path_temp)
        # alldata = ocr.getPoint_BY_PaddleOCRJson(path_temp, "我已")
        # print(alldata)
        # d.click(alldata[0], alldata[1])
        if (str(all_data).count("下一步") > 0):
            # d(text='添加评论...').click()
            print("去")
            point = ocr.getPoint_by_data(all_data, "下一步")
            if (len(point) > 0):
                d.click(point[0], point[1])
                time.sleep(3)
        else:
            return "66"


    for i in range(10):
        d=check_and_reconnect(d,device)
        if (d(textContains="繼續註冊").exists(timeout=5)):
            # d(text="关注").click()
            point_t = get_random_bounds_coord(d(text="繼續註冊").info)
            run_adb_command(device, point_t[0], point_t[1])
            time.sleep(1)
            run_adb_command(device, point_t[0], point_t[1])
            time.sleep(15)
            break
        elif(d(textContains="離開").exists(timeout=3)):

            return "102"#b备注表格 卡号

        if (d(textContains="請填寫驗證碼").exists(timeout=1)):
            break

        path_temp = take_screenshot_white(d)
        all_data = ocr.yewu(path_temp)
        if (str(all_data).count("註冊") > 0):
            point = ocr.getPoint_by_data(all_data, "註冊")
            if (len(point) > 0):
                d.click(point[0], point[1])
                time.sleep(3)
                break
    else:
        print("没有下一步")
        path_temp = take_screenshot_white(d)
        all_data = ocr.yewu(path_temp)
        if (str(all_data).count("註冊") > 0):
            point = ocr.getPoint_by_data(all_data, "註冊")
            if (len(point) > 0):
                d.click(point[0], point[1])
                time.sleep(3)
        if (str(all_data).count("求") > 0 and str(all_data).count("效") > 0):
            return "102"
        else:
            return "66"
    time.sleep(10)
    for i in range(60):
        result_get = send_get_request(list_shuju[1])
        print(f"第{i}次获取验证码，获取的验证码是{result_get}")
        pattern = r'\((\d{6})\)'
        match = re.search(pattern, result_get['data'])
        # 提取结果
        if match:
            verification_code = match.group(1)
            print("提取到的验证码：", verification_code)  # 输出：834227
            break
        time.sleep(3)
    else:
        print("meiyouhuoqudaoyanzhengma")
        return "66"
    for i in range(10):
        d=check_and_reconnect(d, device)
        if (d(textContains="請填寫驗證碼").exists(timeout=3)):
            # d(text="关注").click()
            print("you 請填寫驗證碼")
            d(textContains="請填寫驗證碼").set_text(verification_code)
            time.sleep(3)
            break
        else:
            print("没有输入框")
    else:
        print("11")
        return "66"

    for i in range(10):
        d=check_and_reconnect(d, device)
        if (d(textContains="提交").exists(timeout=3)):
            # d(text="关注").click()
            print("you 提交")
            point_t = get_random_bounds_coord(d(text="提交").info)
            run_adb_command(device, point_t[0], point_t[1])
            time.sleep(1)
            run_adb_command(device, point_t[0], point_t[1])
            time.sleep(3)
            break
    else:
        print("11")
        return "66"
    # d.stop_uiautomator(wait=True)
    no_click = 1
    for i in range(100):
        flag_t = True
        d=check_and_reconnect(d, device)
        print("开始------>",i)
        if (d(textContains="不是我的").exists(timeout=0.2)):
            print("you 不是我的")
            random_click_view(d, d(textContains="不是我的").info)
            time.sleep(2)
            flag_t = False

        if (d(textContains="目前網絡或裝置環境異常").exists(timeout=0.2)):
            # d(text="关注").click()
            print("you 目前網絡或裝置環境異常")
            ThreadSafeExcelHandler.update_cell_by_row_col(row_temp, 4, get_current_time_minute())
            ThreadSafeExcelHandler.update_cell_by_row_col(row_temp, 5, "环境异常")
            visa_ThreadSafeExcelHandler.update_cell_by_row_col(row_t, 5, "环境异常")
            visa_ThreadSafeExcelHandler.update_cell_by_row_col(row_t, 4, get_current_time_minute())
            # random_click_view(d, d(textContains="不是我的").info)
            # time.sleep(2)
            return "101"
            #continue

        if (d(text="允許").exists(timeout=0.2)):
            # d(text="关注").click()
            print("允許通知")
            random_click_view(d, d(text="允許").info)
            #备注手机号注册成功 ，删除当前使用得卡号 visa_ThreadSafeExcelHandler,ThreadSafeExcelHandler
            ThreadSafeExcelHandler.update_cell_by_row_col(row_temp,4,get_current_time_minute())
            ThreadSafeExcelHandler.update_cell_by_row_col(row_temp, 5, "执行成功")
            visa_ThreadSafeExcelHandler.update_cell_by_row_col(row_t,5,"执行成功")
            visa_ThreadSafeExcelHandler.update_cell_by_row_col(row_t, 4, get_current_time_minute())
            time.sleep(2)
            flag_t = False
            #continue
        if (d(textContains="我已閱讀並了解上述內容").exists(timeout=0.2)):
            # d(text="关注").click()
            print("you 我已閱讀並了解上述內容")
            random_click_view(d, d(textContains="我已閱讀並了解上述內容").info)
            time.sleep(2)
            flag_t = False

            if (d(text="下一步").exists(timeout=0.2)):
                # d(text="关注").click()
                print("you text=下一步")
                random_click_view(d, d(text="下一步").info)
                time.sleep(2)
                flag_t = False

            #continue
        if (d(textContains="我已閱讀並同意私隱條款").exists(timeout=0.2)):
            # d(text="关注").click()
            print("you 我已閱讀並同意私隱條款")
            random_click_view(d, d(textContains="我已閱讀並同意私隱條款").info)
            time.sleep(2)
            flag_t = False

            #continue


        if (d(textContains="下一步").exists(timeout=0.2)):
            # d(text="关注").click()
            print("you 下一步")
            random_click_view(d, d(textContains="下一步").info)
            time.sleep(2)
            flag_t = False

            #continue

        if (d(textContains="完成").exists(timeout=0.2)):
            # d(text="关注").click()
            print("you 完成")
            random_click_view(d, d(textContains="完成").info)
            time.sleep(2)
            flag_t = False

            #continue


        if (d(text="取消").exists(timeout=0.2)):
            # d(text="关注").click()
            print("you 取消")
            random_click_view(d, d(text="取消").info)
            time.sleep(2)
            flag_t = False

            #continue

        if (d(text="下一步").exists(timeout=0.2)):
            # d(text="关注").click()
            print("you 取消")
            random_click_view(d, d(text="下一步").info)
            time.sleep(2)
            flag_t = False

            #continue

        if (d(text="同意並啟用").exists(timeout=0.2)):
            # d(text="关注").click()
            print("you 同意並啟用")
            random_click_view(d, d(text="同意並啟用").info)
            time.sleep(2)
            return "1"
        else:
            print("没有 同意並啟用")

        if (d(text="通訊錄").exists(timeout=0.2)):
            # d(text="关注").click()
            print("you 通訊錄")
            #random_click_view(d, d(text="同意並啟用").info)
            time.sleep(2)
            return "1"
        else:
            print("没有 同意並啟用")
        print("flag_t=",flag_t)
        if(flag_t == True):
            no_click += 1
            print("no_click=",no_click)
        if(no_click % 1 == 0 ):
            path_temp = take_screenshot_white(d)
            all_data = ocr.yewu(path_temp)
            # alldata = ocr.getPoint_BY_PaddleOCRJson(path_temp, "我已")
            # print(alldata)
            # d.click(alldata[0], alldata[1])
            if (str(all_data).count("目前") > 0 and str(all_data).count("或") > 0):
                # d(text="关注").click()
                print("you 目前網絡或裝置環境異常")
                ThreadSafeExcelHandler.update_cell_by_row_col(row_temp, 4, get_current_time_minute())
                ThreadSafeExcelHandler.update_cell_by_row_col(row_temp, 5, "环境异常")
                visa_ThreadSafeExcelHandler.update_cell_by_row_col(row_t, 5, "环境异常")
                visa_ThreadSafeExcelHandler.update_cell_by_row_col(row_t, 4, get_current_time_minute())
                # random_click_view(d, d(textContains="不是我的").info)
                # time.sleep(2)
                return "101"

            if (str(all_data).count("我已") > 0):
                # d(text='添加评论...').click()
                print("我已")
                point = ocr.getPoint_by_data(all_data, "我已")
                if (len(point) > 0):
                    d.click(point[0], point[1])
                    time.sleep(3)

                    if (str(all_data).count("下一步") > 0):
                        # d(text='添加评论...').click()
                        print("下一步")
                        point = ocr.getPoint_by_data_true(all_data, "下一步")
                        if (len(point) > 0):
                            d.click(point[0], point[1])
                            time.sleep(3)
                    if (str(all_data).count("完成") > 0):
                        # d(text='添加评论...').click()
                        print("下一步")
                        point = ocr.getPoint_by_data_true(all_data, "完成")
                        if (len(point) > 0):
                            d.click(point[0], point[1])
                            time.sleep(3)
            if (str(all_data).count("下一步") > 0):
                # d(text='添加评论...').click()
                print("下一步")
                point = ocr.getPoint_by_data_true(all_data, "下一步")
                if (len(point) > 0):
                    d.click(point[0], point[1])
                    time.sleep(3)
            if (str(all_data).count("同意") > 0):
                # d(text='添加评论...').click()
                print("同意")
                point = ocr.getPoint_by_data_back(all_data, "同意")
                if (len(point) > 0):
                    d.click(point[0], point[1])
                    time.sleep(3)



ocr = OCRProcessor()#網頁無法使用
#devices = ["192.168.11.163:5001","192.168.11.163:5002","192.168.11.163:5003","192.168.11.163:5004","192.168.11.163:5005",
#            "192.168.11.163:5006","192.168.11.163:5007","192.168.11.163:5008","192.168.11.163:5009","192.168.11.163:5010",
#            "192.168.11.163:5011","192.168.11.163:5012","192.168.11.163:5013","192.168.11.163:5014","192.168.11.163:5015"]
#devices = ["192.168.11.214:5001"]
devices = ["192.168.11.214:5006","192.168.11.214:5007","192.168.11.214:5008","192.168.11.214:5009","192.168.11.214:5010"]
shoujihao_ThreadSafeExcelHandler = ThreadSafeExcelHandler(r"C:\Users\11009\Desktop\测试.xlsx")
visa_ThreadSafeExcelHandler = ThreadSafeExcelHandler(r"C:\Users\11009\Desktop\visa.xlsx")
# row1 = ThreadSafeExcelHandler.get_row(2)
# list1,row2 = ThreadSafeExcelHandler.get_first_row_with_empty_3rd_4th()
# ThreadSafeExcelHandler.update_cell_by_row_col(row2,3,"meng")
# ThreadSafeExcelHandler.update_cell_by_row_col(row2,4,"meng2")
# print(list1,row2)

#
# if (d(text="依次點擊").exists(timeout=3)):
#     print("依次點擊")
#result_reg = register("192.168.11.214:5015", ThreadSafeExcelHandler, ocr)

def yewu_most(device,ThreadSafeExcelHandler,ocr):
    huanhao_flag = True
    visa_flag = True
    while(True):
        if(huanhao_flag == True):
            row1 = ThreadSafeExcelHandler.get_first_row_with_empty_3rd_4th()
            print(row1)
        if (row1 is None):
            return "99"
        huanhao_flag = False
        list_shuju, row_temp = row1
        ThreadSafeExcelHandler.update_cell_by_row_col(row_temp, 3, "执行中")
        result_reg = register(device, row1, ocr)
        if(result_reg == "101"):
            huanhao_flag = True #换手机号
        elif (result_reg != "1"):
            continue
        # print(find_coords_by_text(d,"依次點擊："))
        result_jiaoyan = jiaoyanma(device)
        if (result_jiaoyan == "101"):
            huanhao_flag = True  # 换手机号
        elif (result_jiaoyan != "1"):
            continue

        if(visa_flag == True):
            result_t = visa_ThreadSafeExcelHandler.get_first_row_with_empty_4rd_5th()
            if (result_t is None):
                return "99"
        visa_flag = False
        result_card = check_bank_cark(device, visa_ThreadSafeExcelHandler, ThreadSafeExcelHandler, list_shuju, row_temp,result_t)
        if (result_card == "101"):
            huanhao_flag = True  # 换手机号
        elif(result_card == "102"):
            visa_ThreadSafeExcelHandler.update_cell_by_row_col(row_temp, 4, "请求无效")
            visa_ThreadSafeExcelHandler.update_cell_by_row_col(row_temp, 5, get_current_time_minute())
            visa_flag = True
        elif (result_card != "1"):
            continue

        # if (result_card == "102"):
        #     visa_ThreadSafeExcelHandler.update_cell_by_row_col(row_temp, 4, "请求无效")
        #     return "66"

def jincheng():
    for device in devices:
        print("qidong--->", device)
        th = threading.Thread(target=yewu_most, args=(device, shoujihao_ThreadSafeExcelHandler, ocr))
        th.start()
        time.sleep(1)
threading.Thread(target=jincheng).start()

