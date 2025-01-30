import axios from "axios";

const API_URL = process.env.VUE_APP_API_URL
  ? process.env.VUE_APP_API_URL
  : "/api";
const TOKEN = process.env.VUE_APP_API_TOKEN;

function stripUrl(url) {
  if (url.indexOf("api") > -1) {
    return "/" + url.substring(url.indexOf("api"));
  }
  return url;
}

/*
 *Static API Data
 * Used when VUE_APP_API_URL = STATIC
 */
const documents = {
  count: 1490,
  next: "http://sharc-autharch-stg.kdl.kcl.ac.uk/api/documents/?format=json&page=2",
  previous: null,
  facets: {
    _filter_text: {
      doc_count: 1490,
      text: {
        doc_count_error_upper_bound: 0,
        sum_other_doc_count: 0,
        buckets: [
          { key: "Adaptation", doc_count: 15 },
          { key: "Book", doc_count: 328 },
          { key: "Character", doc_count: 2 },
          { key: "Character - Identification", doc_count: 129 },
          { key: "Character - Portrait", doc_count: 40 },
          { key: "Character Portrait", doc_count: 21 },
          { key: "Quotation", doc_count: 23 },
          { key: "Reading", doc_count: 82 },
          { key: "Scene depiction", doc_count: 82 },
          { key: "Text", doc_count: 18 },
          { key: "Translation", doc_count: 53 },
        ],
      },
    },
    _filter_category: {
      doc_count: 1490,
      category: {
        doc_count_error_upper_bound: 0,
        sum_other_doc_count: 0,
        buckets: [
          { key: "Album", doc_count: 4 },
          { key: "Banknote", doc_count: 1 },
          { key: "Book", doc_count: 486 },
          { key: "Book of prints", doc_count: 1 },
          { key: "CD", doc_count: 1 },
          { key: "Coin", doc_count: 4 },
          { key: "Decorative Arts", doc_count: 4 },
          { key: "Decorative arts", doc_count: 27 },
          { key: "Drawing", doc_count: 44 },
          { key: "Medals", doc_count: 4 },
          { key: "Miniature", doc_count: 5 },
          { key: "None", doc_count: 50 },
          { key: "Painting", doc_count: 58 },
          { key: "Photograph", doc_count: 148 },
          { key: "Photograph Album", doc_count: 1 },
          { key: "Photograph ", doc_count: 1 },
          { key: "Print", doc_count: 642 },
          { key: "Print group", doc_count: 1 },
          { key: "Print series", doc_count: 1 },
          { key: "Print ", doc_count: 2 },
          { key: "Tapestry", doc_count: 1 },
          { key: "Works of art", doc_count: 4 },
        ],
      },
    },
    _filter_source: {
      doc_count: 1490,
      source: {
        doc_count_error_upper_bound: 0,
        sum_other_doc_count: 0,
        buckets: [
          { key: "Book", doc_count: 7 },
          { key: "Scene Depiction", doc_count: 1 },
          { key: "Scene depiction", doc_count: 4 },
        ],
      },
    },
    _filter_work: {
      doc_count: 1490,
      work: {
        doc_count_error_upper_bound: 0,
        sum_other_doc_count: 0,
        buckets: [
          { key: "", doc_count: 9 },
          { key: "1 & 2 Henry IV", doc_count: 1 },
          { key: "1 Henry IV", doc_count: 15 },
          { key: "1 Henry VI", doc_count: 8 },
          { key: "2 Henry IV", doc_count: 17 },
          { key: "2 Henry VI", doc_count: 9 },
          { key: "3 Henry VI", doc_count: 5 },
          { key: "A Midsummer Night's Dream", doc_count: 38 },
          { key: "All's Well That Ends Well", doc_count: 5 },
          { key: "All's Well that Ends Well", doc_count: 7 },
          { key: "All's Well the Ends Well", doc_count: 1 },
          { key: "Antony and Cleopatra", doc_count: 11 },
          { key: "Apocrypha", doc_count: 3 },
          { key: "As You Like It", doc_count: 37 },
          { key: "Character", doc_count: 19 },
          { key: "Comedy of Errors", doc_count: 5 },
          { key: "Coriolanus", doc_count: 16 },
          { key: "Cymbeline", doc_count: 9 },
          { key: "Forgeries", doc_count: 16 },
          { key: "Hamlet", doc_count: 101 },
          { key: "Henry IV part 1", doc_count: 9 },
          { key: "Henry IV part 2", doc_count: 7 },
          { key: "Henry V", doc_count: 26 },
          { key: "Henry VI part 1", doc_count: 6 },
          { key: "Henry VI part 2", doc_count: 8 },
          { key: "Henry VI part 3", doc_count: 4 },
          { key: "Henry VIII", doc_count: 47 },
          { key: "Individual", doc_count: 1 },
          { key: "Julius Caesar", doc_count: 23 },
          { key: "King John", doc_count: 46 },
          { key: "King Lear", doc_count: 34 },
          { key: "Love's Labour's Lost", doc_count: 4 },
          { key: "Love's Labours Lost", doc_count: 6 },
          { key: "Macbeth", doc_count: 66 },
          { key: "Measure for Measure", doc_count: 13 },
          { key: "Merchant of Venice", doc_count: 2 },
          { key: "Much Ado About Nothing", doc_count: 33 },
          { key: "Othello", doc_count: 26 },
          { key: "Pericles", doc_count: 5 },
          { key: "Plays", doc_count: 4 },
          { key: "Richard II", doc_count: 77 },
          { key: "Richard III", doc_count: 86 },
          { key: "Romeo and Juliet", doc_count: 77 },
          { key: "Sonnets", doc_count: 10 },
          { key: "The Comedy of Errors", doc_count: 15 },
          { key: "The Merchant of Venice", doc_count: 36 },
          { key: "The Merry Wives of Windsor", doc_count: 68 },
          { key: "The Rape of Lucrece", doc_count: 1 },
          { key: "The Taming of the Shrew", doc_count: 16 },
          { key: "The Tempest", doc_count: 41 },
          { key: "The Two Gentlemen of Verona", doc_count: 6 },
          { key: "The Winter's Tale", doc_count: 65 },
          { key: "Timon of Athens", doc_count: 14 },
          { key: "Titus Andronicus", doc_count: 11 },
          { key: "Troilus and Cressida", doc_count: 8 },
          { key: "Twelfth Night", doc_count: 21 },
          { key: "Two Gentlemen of Verona", doc_count: 5 },
          { key: "Venus and Adonis", doc_count: 6 },
        ],
      },
    },
    _filter_acquirer: {
      doc_count: 1490,
      acquirer: {
        doc_count_error_upper_bound: 0,
        sum_other_doc_count: 0,
        buckets: [
          { key: "Albert, Prince Consort (1819-61)", doc_count: 2 },
          { key: "Alfred, Duke of Edinburgh (1844-1900)", doc_count: 9 },
          {
            key: "Antonio Ghiringhelli (1906-79) Queen Elizabeth II (b 1926), Queen of Great Britain and Northern Ireland",
            doc_count: 1,
          },
          { key: "Charles II (1630-85)", doc_count: 1 },
          { key: "David Garrick (1717-79)", doc_count: 2 },
          { key: "Edward, Prince of Wales (1841-1910)", doc_count: 1 },
          {
            key: "Ellen Terry (1847-1928) Queen Mary (1867-1953), consort of George V",
            doc_count: 39,
          },
          { key: "Ernest, Duke of Cumberland (1771-1851)", doc_count: 1 },
          {
            key: "Fred Whitehead (1853-1938) Queen Mary (1867-1953), consort of George V",
            doc_count: 1,
          },
          {
            key: "Frederica Charlotte, Duchess of York (1767-1820)",
            doc_count: 1,
          },
          { key: "George III (1738-1820)", doc_count: 11 },
          { key: "George IV (1762-1830)", doc_count: 12 },
          { key: "George V (1865-1936)", doc_count: 1 },
          { key: "George VI (1895-1952)", doc_count: 2 },
          { key: "George, Prince Regent (1762-1830)", doc_count: 7 },
          { key: "George, Prince of Wales (1762-1820)", doc_count: 3 },
          { key: "George, Prince of Wales (1762-1830)", doc_count: 17 },
          { key: "Harry Lloyd Verney (1872-1950)", doc_count: 1 },
          {
            key: "James Orchard Halliwell-Phillipps (1820-89) Queen Victoria (1819-1901), Queen of Great Britain and Ireland",
            doc_count: 1,
          },
          {
            key: "Joseph Leeson, 1st Earl of Milltown (1711-1783)",
            doc_count: 1,
          },
          {
            key: "King Charles I (1600-49), King of England, Scotland and Ireland",
            doc_count: 1,
          },
          {
            key: "King Edward VII (1841-1910), King of Great Britain and Ireland",
            doc_count: 7,
          },
          {
            key: "King George III (1738-1820), King of Great Britain and Ireland",
            doc_count: 22,
          },
          {
            key: "King George IV (1762-1830), King of Great Britain and Ireland",
            doc_count: 3,
          },
          {
            key: "King George V (1865-1936), King of Great Britain and Ireland",
            doc_count: 12,
          },
          {
            key: "King George VI (1895-1952), King of Great Britain and Ireland",
            doc_count: 1,
          },
          {
            key: "King WIlliam IV (1765-1837), King of Great Britain and Ireland",
            doc_count: 1,
          },
          {
            key: "King William IV (1765-1837), King of Great Britain and Ireland",
            doc_count: 3,
          },
          { key: "Louise, Duchess of Connaught (1860-1917)", doc_count: 1 },
          { key: "Prince Albert (1819-1862)", doc_count: 1 },
          { key: "Prince Albert (1819-61)", doc_count: 4 },
          { key: "Prince Albert (1819-61), Prince Consort", doc_count: 1 },
          {
            key: "Prince Albert (1819-61), Prince Consort to Victoria",
            doc_count: 23,
          },
          {
            key: "Prince Albert Edward (1841-1910), Prince of Wales",
            doc_count: 5,
          },
          { key: "Prince Arthur (1850-1942)", doc_count: 1 },
          { key: "Prince George (1762-1830), Prince Regent", doc_count: 26 },
          { key: "Prince George (1762-1830), Prince of Wales", doc_count: 72 },
          { key: "Prince George of Wales (1865-1936)", doc_count: 1 },
          {
            key: "Prince Philip (b 1921), Duke of Edinburgh, consort of Elizabeth II",
            doc_count: 1,
          },
          { key: "Princess Alexandra of Wales (1844-1925)", doc_count: 1 },
          {
            key: "Princess Elizabeth (b 1926), Duchess of Edinburgh",
            doc_count: 10,
          },
          { key: "Princess Helena (1846-1923)", doc_count: 1 },
          {
            key: "Princess Marie Louise of Schleswig-Holstein (1872-1956)",
            doc_count: 2,
          },
          { key: "Princess Mary (1867-1953), Princess of Wales", doc_count: 1 },
          { key: "Princess May of Teck (1867-1953)", doc_count: 8 },
          { key: "Queen Adelaide (1792-1849)", doc_count: 1 },
          { key: "Queen Caroline (1683-1747)", doc_count: 1 },
          { key: "Queen Charlotte (1744-1718)", doc_count: 4 },
          { key: "Queen Charlotte (1744-1814)", doc_count: 2 },
          { key: "Queen Charlotte (1744-1818)", doc_count: 92 },
          { key: "Queen Charlotte (1844-1818)", doc_count: 1 },
          {
            key: "Queen Elizabeth (1900-2002), the Queen Mother",
            doc_count: 1,
          },
          {
            key: "Queen Elizabeth II (b 1926), Queen of Great Britain and Northern Ireland",
            doc_count: 54,
          },
          { key: "Queen Elizabeth II (b.1926)", doc_count: 10 },
          { key: "Queen Elizabeth the Queen Mother (1900-2002)", doc_count: 4 },
          { key: "Queen Mary (1867-1953)", doc_count: 5 },
          { key: "Queen Mary (1867-1953), consort of George V", doc_count: 5 },
          { key: "Queen Victoria (1819-1901)", doc_count: 53 },
          {
            key: "Queen Victoria (1819-1901), Queen of Great Britain and Ireland",
            doc_count: 51,
          },
          { key: "Sir Fleetwood Edwards (1842-1910)", doc_count: 1 },
          {
            key: "Sir Thomas Dennehy (1829-1915) Queen Victoria (1819-1901), Queen of Great Britain and Ireland",
            doc_count: 2,
          },
          { key: "William IV (1765-1837)", doc_count: 1 },
        ],
      },
    },
    _filter_performance: {
      doc_count: 1490,
      performance: {
        doc_count_error_upper_bound: 0,
        sum_other_doc_count: 0,
        buckets: [
          { key: "Actor Portrait", doc_count: 34 },
          { key: "Adaptation", doc_count: 1 },
          { key: "Character - Actor Portrait", doc_count: 1 },
          { key: "Character - Identification", doc_count: 30 },
          { key: "Character - Portrait", doc_count: 396 },
          { key: "Character Portrait", doc_count: 1 },
          { key: "Performance", doc_count: 9 },
          { key: "Performance record", doc_count: 72 },
          { key: "Scene depiction", doc_count: 314 },
        ],
      },
    },
    _filter_individual_connections: {
      doc_count: 1490,
      individual_connections: {
        doc_count_error_upper_bound: 0,
        sum_other_doc_count: 0,
        buckets: [
          { key: "Biographical", doc_count: 13 },
          { key: "Biographies", doc_count: 23 },
          { key: "Biography", doc_count: 2 },
          { key: "Context", doc_count: 5 },
          { key: "Individual", doc_count: 8 },
          { key: "Institutions", doc_count: 4 },
          { key: "Locations", doc_count: 12 },
          { key: "Locations - London", doc_count: 5 },
          { key: "Locations - Stratford", doc_count: 14 },
          { key: "Portraits", doc_count: 1 },
          { key: "Portraits and bust", doc_count: 1 },
          { key: "Portraits and busts", doc_count: 88 },
          { key: "Potraits and busts", doc_count: 2 },
          { key: "Relics", doc_count: 9 },
          { key: "Works", doc_count: 4 },
          { key: "Works - Plays", doc_count: 3 },
        ],
      },
    },
  },
  results: [
    {
      pk: 1094,
      reference: "1059094",
      unittitle: "A Book of homage to Shakespeare",
      category: "Book",
      size: "1 item; 30.0 x 6.0 cm",
      medium: "book, half leather bound in vellum",
      label: "[inside cover] Bookplate of King George V.",
      creators: [
        { key: "persnames-459", name: "Sir Israel Gollancz (1863-1930)" },
      ],
      date_of_creation: [1916],
      place_of_origin: [],
      date_of_acquisition: [
        1916, 1917, 1918, 1919, 1920, 1921, 1922, 1923, 1924, 1925, 1926, 1927,
        1928, 1929, 1930, 1931, 1932, 1933, 1934, 1935, 1936,
      ],
      related_material: "",
      related_sources: {
        individuals: ["Institutions"],
        works: [],
        texts: ["Reading"],
        sources: [],
        performances: [],
      },
      related_people: {
        acquirers: [
          "King George V (1865-1936), King of Great Britain and Ireland",
        ],
        donors: [],
        publishers: [],
      },
      media: [
        {
          label: "1",
          iiif_manifest_url: "/rct/iiif/732115a/",
          iiif_image_url: "/rct/iiif/image/34658",
          full_image_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/max/0/default.jpg",
          thumbnail_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
          image_width: 4015,
          image_height: 2980,
          thumbnail_width: 175,
          thumbnail_height: 130,
        },
      ],
      search_content:
        " A Book of homage to Shakespeare 1059094 Book ['Works', 'Text', 'Reading'] [inside cover] Bookplate of King George V.",
      doc_type: "object",
    },
    {
      pk: 1026,
      reference: "1059011",
      unittitle:
        "A Catalogue of pictures etc. in the Shakspeare Gallery, Pall Mall.",
      category: "Book",
      size: "1 item; 20.5 x 1.5 cm",
      medium: "book; half leather bound in red morocco",
      label: "[inside cover] Bookplate of Royal Library, 1863-1901",
      creators: [
        { key: "persnames-423", name: "John Boydell (1720-1804)" },
        { key: "persnames-424", name: "Josiah Boydell (1752-1817)" },
      ],
      date_of_creation: [1810],
      place_of_origin: [],
      date_of_acquisition: [1810],
      related_material: "",
      related_sources: {
        individuals: [],
        works: ["Plays"],
        texts: ["Scene depiction"],
        sources: [],
        performances: ["Scene depiction"],
      },
      related_people: { acquirers: [], donors: [], publishers: [] },
      media: [
        {
          label: "1",
          iiif_manifest_url: "/rct/iiif/732115a/",
          iiif_image_url: "/rct/iiif/image/34658",
          full_image_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/max/0/default.jpg",
          thumbnail_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
          image_width: 4015,
          image_height: 2980,
          thumbnail_width: 175,
          thumbnail_height: 130,
        },
      ],
      search_content:
        " A Catalogue of pictures etc. in the Shakspeare Gallery, Pall Mall. 1059011 Book ['Works', 'Performance', 'Scene depiction'] [inside cover] Bookplate of Royal Library, 1863-1901",
      doc_type: "object",
    },
    {
      pk: 2210,
      reference: "981237",
      unittitle: "A Character from Richard II",
      category: "Drawing",
      size: "1 item; 26.8 x 16.7 cm (sheet of paper)",
      medium: "Pencil, watercolour, touches of body colour",
      label: "Inscribed lower right: 'V. June 6. 1857'",
      creators: [
        { key: "persnames-1162", name: "Princess Victoria (1840-1901)" },
      ],
      date_of_creation: [1857],
      place_of_origin: [],
      date_of_acquisition: [1857],
      related_material: "",
      related_sources: {
        individuals: [],
        works: ["Richard II"],
        texts: [],
        sources: [],
        performances: ["Performance record"],
      },
      related_people: { acquirers: [], donors: [], publishers: [] },
      media: [
        {
          label: "1",
          iiif_manifest_url: "/rct/iiif/732115a/",
          iiif_image_url: "/rct/iiif/image/34658",
          full_image_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/max/0/default.jpg",
          thumbnail_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
          image_width: 4015,
          image_height: 2980,
          thumbnail_width: 175,
          thumbnail_height: 130,
        },
      ],
      search_content:
        " A Character from Richard II 981237 Drawing ['Works', 'Performance', 'Performance record'] Inscribed lower right: 'V. June 6. 1857'",
      doc_type: "object",
    },
    {
      pk: 1084,
      reference: "1059081",
      unittitle:
        "A Chronicle history of the life and work of William Shakespeare, player, poet and playmaker",
      category: "Book",
      size: "1 item; 23.5 x 4.0 cm",
      medium: "book, quarter leather bound in black morocco",
      label: "None",
      creators: [
        { key: "persnames-454", name: "Frederick Gard Fleay (1831-1909)" },
      ],
      date_of_creation: [1886],
      place_of_origin: [],
      date_of_acquisition: [1886],
      related_material: "",
      related_sources: {
        individuals: [],
        works: [],
        texts: ["Reading"],
        sources: [],
        performances: [],
      },
      related_people: { acquirers: [], donors: [], publishers: [] },
      media: [
        {
          label: "1",
          iiif_manifest_url: "/rct/iiif/732115a/",
          iiif_image_url: "/rct/iiif/image/34658",
          full_image_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/max/0/default.jpg",
          thumbnail_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
          image_width: 4015,
          image_height: 2980,
          thumbnail_width: 175,
          thumbnail_height: 130,
        },
      ],
      search_content:
        " A Chronicle history of the life and work of William Shakespeare, player, poet and playmaker 1059081 Book ['Works', 'Text', 'Reading'] None",
      doc_type: "object",
    },
    {
      pk: 2116,
      reference: "817106",
      unittitle:
        "A Collection of Prints from pictures painted for the purpose of illustrating the Dramatic Works of Shakspeare",
      category: "Book of prints",
      size: "1 item; None",
      medium:
        "Two volumes bound together, in a beige cloth cover with a brown leather spine and corners.",
      label: "None",
      creators: [
        { key: "persnames-1092", name: "Anne Seymour Damer (1748-1828)" },
        { key: "persnames-788", name: "William Satchwell Leney (1769-1831)" },
        { key: "persnames-959", name: "Thomas Banks (1735-1805)" },
        { key: "persnames-960", name: " Benjamin Smith (fl. 1786-1833)" },
        { key: "persnames-781", name: "George Romney (1734-1802)" },
        { key: "persnames-1077", name: "Henry Fuseli (1741-1825)" },
        { key: "persnames-1093", name: "Jean Pierre Simon (c.1764-1813)" },
        { key: "persnames-1094", name: "Robert Thew (1758-1802)" },
        { key: "persnames-1095", name: "Joseph Wright (1734-1797)" },
        { key: "persnames-1096", name: "Caroline Watson (c.1761-1814)" },
        { key: "persnames-882", name: "Francis Wheatley (1747-1801)" },
        { key: "persnames-621", name: "Luigi Schiavonetti (1765-1810)" },
        { key: "persnames-1097", name: "Angelica Kauffman (1741-1807)" },
        { key: "persnames-1098", name: "Robert Smirke (1753-1845)" },
        { key: "persnames-1099", name: "William Peters (1742-1814)" },
        { key: "persnames-1100", name: "Matthew Peters (1741" },
        { key: "persnames-1101", name: "Thomas Ryder (1745-1810)" },
        { key: "persnames-1102", name: "James Durno (c.1745-1795)" },
        { key: "persnames-765", name: "Isaac Taylor (1759-1829)" },
        { key: "persnames-1103", name: "Thomas Kirk (1765-1797)" },
        {
          key: "persnames-1104",
          name: "Charles Gauthier Playter (fl. 1786-1809)",
        },
        { key: "persnames-1105", name: "John Francis Rigaud (1742-1810)" },
        { key: "persnames-860", name: "William Hamilton (1751-1801)" },
        { key: "persnames-746", name: "John Ogborne (1755-1837)" },
        { key: "persnames-1106", name: "John Browne (1742-1801)" },
        { key: "persnames-1107", name: "William Hodges (1744-1797)" },
        { key: "persnames-1108", name: "John Downman (1750-1824)" },
        { key: "persnames-1109", name: "Samuel Middiman (1750-1831)" },
        { key: "persnames-1110", name: "William Wilson (fl. 1750-94)" },
        { key: "persnames-1111", name: "Raphael Lamar West (1766-1850)" },
        {
          key: "persnames-1112",
          name: "Georg Siegmund Facius (c.1750-c.1813)",
        },
        { key: "persnames-1113", name: "Johann Gottlieb Facius (b.c.1750)" },
        { key: "persnames-1114", name: "James Fittler (1758-1835)" },
        { key: "persnames-634", name: "Johann Heinrich Ramberg (1763-1840)" },
        { key: "persnames-630", name: "Francesco Bartolozzi (1727-1815)" },
        { key: "persnames-574", name: "John Opie (1761-1807)" },
        { key: "persnames-882", name: "Francis Wheatley (1747-1801)" },
        { key: "persnames-1109", name: "Samuel Middiman (1750-1831)" },
        { key: "persnames-763", name: "James Caldwell (1739-1822)" },
        { key: "persnames-1115", name: "James Parker (1750 - 1805)" },
        { key: "persnames-622", name: "Sir Joshua Reynolds (1723-92)" },
        { key: "persnames-1116", name: "Petro William Tomkins (1759-1840)" },
        { key: "persnames-746", name: "John Ogborne (1755-1837)" },
        { key: "persnames-1117", name: "Thomas Hellyer (b.c.1771)" },
        { key: "persnames-1092", name: "Anne Seymour Damer (1748-1828)" },
        { key: "persnames-1118", name: "William Beechey (1753-1839)" },
        { key: "persnames-664", name: "James Northcote (1746-1831)" },
        { key: "persnames-1119", name: "Mather Browne (1761-1831)" },
        { key: "persnames-323", name: "Joseph Farington (1747-1821)" },
        { key: "persnames-1026", name: "Richard Westall (1765-1836)" },
        { key: "persnames-1120", name: "James Durno (c.1745-95)" },
        { key: "persnames-424", name: "Josiah Boydell (1752-1817)" },
        { key: "persnames-746", name: "John Ogborne (1755-1837)" },
        { key: "persnames-1121", name: "Jean Baptiste Michel (c.1780-1804)" },
        { key: "persnames-1122", name: "William Miller (c.1740-1810)" },
        { key: "persnames-1123", name: "Francis Legat (1755-1809)" },
        { key: "persnames-707", name: "William Skelton (1763-1848)" },
        { key: "persnames-1124", name: "Joseph Collyer (1748-1827)" },
        { key: "persnames-1125", name: "Gavin Hamilton (1723-1798)" },
        { key: "persnames-659", name: "Edward Scriven (1775-1841)" },
        { key: "persnames-1126", name: "Henry Tresham (c.1751-1814)" },
        { key: "persnames-1127", name: "Thomas Kirk (c.1767-97)" },
        { key: "persnames-538", name: "Thomas Burke (1749-1815)" },
        { key: "persnames-1128", name: "John Hoppner (1758-1810)" },
        { key: "persnames-615", name: "William Sharp (1749-1824)" },
        { key: "persnames-1129", name: "Benjamin West (1838-1820)" },
        { key: "persnames-1130", name: "James Barry (1741-1806)" },
        { key: "persnames-787", name: "John Graham (1754-1817)" },
        { key: "persnames-1131", name: "Thomas Gaugain (1756-1812)" },
      ],
      date_of_creation: [1805],
      place_of_origin: [],
      date_of_acquisition: [1805],
      related_material: "",
      related_sources: {
        individuals: [],
        works: [],
        texts: ["Scene depiction"],
        sources: [],
        performances: [],
      },
      related_people: {
        acquirers: ["George, Prince of Wales (1762-1830)"],
        donors: [],
        publishers: ["Josiah Boydell (1752-1817)"],
      },
      media: [
        {
          label: "1",
          iiif_manifest_url: "/rct/iiif/732115a/",
          iiif_image_url: "/rct/iiif/image/34658",
          full_image_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/max/0/default.jpg",
          thumbnail_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
          image_width: 4015,
          image_height: 2980,
          thumbnail_width: 175,
          thumbnail_height: 130,
        },
      ],
      search_content:
        " A Collection of Prints from pictures painted for the purpose of illustrating the Dramatic Works of Shakspeare 817106 Book of prints ['Works', 'Text', 'Scene depiction'] None",
      doc_type: "object",
    },
    {
      pk: 962,
      reference: "1058901",
      unittitle:
        "A Complete verbal index to the plays of Shakespeare adapted to all editions comprehending every substantive, adjective, verb, participle and adverb used by Shakespeare ; vol. 1",
      category: "Book",
      size: "1 item; 22.0 x 5.0 cm",
      medium: "book",
      label:
        '[flyleaf] "May 26 1842 | Archdeacon Todd told me just | now that he had seen this book | in a Bookseller\'s catalogue marked | at 5.10. - | William Nicol " QQQQQ [half title page] " Given to me by my | worthy friend Danl Braithwait | G.N. | Decr 28 1807 "',
      creators: [
        { key: "persnames-390", name: "Francis Twiss (c 1759 -1827)" },
      ],
      date_of_creation: [1805],
      place_of_origin: [],
      date_of_acquisition: [1842],
      related_material: "",
      related_sources: {
        individuals: [],
        works: [],
        texts: ["Reading"],
        sources: [],
        performances: [],
      },
      related_people: {
        acquirers: [
          "Queen Victoria (1819-1901), Queen of Great Britain and Ireland",
        ],
        donors: [],
        publishers: [],
      },
      media: [
        {
          label: "3",
          iiif_manifest_url: "https://rct.resourcespace.com/iiif/1058901/",
          iiif_image_url: "/rct/iiif/image/52743",
          full_image_url:
            "https://rct.resourcespace.com/iiif/image/52743/full/max/0/default.jpg",
          thumbnail_url:
            "https://rct.resourcespace.com/iiif/image/52743/full/thm/0/default.jpg",
          image_width: 2563,
          image_height: 3523,
          thumbnail_width: 127,
          thumbnail_height: 175,
        },
      ],
      search_content:
        " A Complete verbal index to the plays of Shakespeare adapted to all editions comprehending every substantive, adjective, verb, participle and adverb used by Shakespeare ; vol. 1 1058901 Book ['Works', 'Text', 'Reading'] [flyleaf] \"May 26 1842 | Archdeacon Todd told me just | now that he had seen this book | in a Bookseller's catalogue marked | at 5.10. - | William Nicol \" QQQQQ [half title page] \" Given to me by my | worthy friend Danl Braithwait | G.N. | Decr 28 1807 \"",
      doc_type: "object",
    },
    {
      pk: 963,
      reference: "1058902",
      unittitle:
        "A Complete verbal index to the plays of Shakespeare adapted to all editions comprehending every substantive, adjective, verb, participle and adverb used by Shakespeare ; vol. 2",
      category: "Book",
      size: "1 item; 22.0 x 5.0 cm",
      medium: "book",
      label: "None",
      creators: [
        { key: "persnames-390", name: "Francis Twiss (c 1759 -1827)" },
      ],
      date_of_creation: [1805],
      place_of_origin: [],
      date_of_acquisition: [1842],
      related_material: "",
      related_sources: {
        individuals: [],
        works: [],
        texts: ["Reading"],
        sources: [],
        performances: [],
      },
      related_people: {
        acquirers: [
          "Queen Victoria (1819-1901), Queen of Great Britain and Ireland",
        ],
        donors: [],
        publishers: [],
      },
      media: [
        {
          label: "1",
          iiif_manifest_url: "/rct/iiif/732115a/",
          iiif_image_url: "/rct/iiif/image/34658",
          full_image_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/max/0/default.jpg",
          thumbnail_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
          image_width: 4015,
          image_height: 2980,
          thumbnail_width: 175,
          thumbnail_height: 130,
        },
      ],
      search_content:
        " A Complete verbal index to the plays of Shakespeare adapted to all editions comprehending every substantive, adjective, verb, participle and adverb used by Shakespeare ; vol. 2 1058902 Book ['Works', 'Text', 'Reading'] None",
      doc_type: "object",
    },
    {
      pk: 1093,
      reference: "1059093",
      unittitle: "A Dictionary of the language of Shakspeare",
      category: "Book",
      size: "1 item; 29.5 x 3.5 cm",
      medium: "book",
      label: "[inside cover] Bookplate of Royal Library, 1863-1901",
      creators: [{ key: "persnames-458", name: "Swynfen Jervis (1798-1867)" }],
      date_of_creation: [1868],
      place_of_origin: [],
      date_of_acquisition: [1868],
      related_material: "",
      related_sources: {
        individuals: [],
        works: [],
        texts: ["Reading"],
        sources: [],
        performances: [],
      },
      related_people: { acquirers: [], donors: [], publishers: [] },
      media: [
        {
          label: "1",
          iiif_manifest_url: "/rct/iiif/732115a/",
          iiif_image_url: "/rct/iiif/image/34658",
          full_image_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/max/0/default.jpg",
          thumbnail_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
          image_width: 4015,
          image_height: 2980,
          thumbnail_width: 175,
          thumbnail_height: 130,
        },
      ],
      search_content:
        " A Dictionary of the language of Shakspeare 1059093 Book ['Works', 'Text', 'Reading'] [inside cover] Bookplate of Royal Library, 1863-1901",
      doc_type: "object",
    },
    {
      pk: 981,
      reference: "1058921",
      unittitle: "A Few notes on Shakespeare",
      category: "Book",
      size: "1 item; 23.5 x 1.2 x 15.1 cm",
      medium: "book",
      label: "None",
      creators: [{ key: "persnames-314", name: "Alexander Dyce (1798-1869)" }],
      date_of_creation: [1853],
      place_of_origin: [],
      date_of_acquisition: [],
      related_material: "",
      related_sources: {
        individuals: [],
        works: ["Forgeries"],
        texts: ["Reading"],
        sources: [],
        performances: [],
      },
      related_people: { acquirers: [], donors: [], publishers: [] },
      media: [
        {
          label: "1",
          iiif_manifest_url: "/rct/iiif/732115a/",
          iiif_image_url: "/rct/iiif/image/34658",
          full_image_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/max/0/default.jpg",
          thumbnail_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
          image_width: 4015,
          image_height: 2980,
          thumbnail_width: 175,
          thumbnail_height: 130,
        },
      ],
      search_content:
        " A Few notes on Shakespeare 1058921 Book ['Works', 'Text', 'Reading'] None",
      doc_type: "object",
    },
    {
      pk: 960,
      reference: "1058899",
      unittitle:
        "A Glossary or collection of words, phrases, names and allusions to customs, proverbs etc ... in the works of English Authors particularly Shakespeare and his contemporaries ; vol. 1",
      category: "Book",
      size: "1 item; 24.0 x 4.0 cm",
      medium: "book",
      label: "None",
      creators: [
        { key: "persnames-387", name: "Robert Nares (1753-1829)" },
        {
          key: "persnames-388",
          name: "James Orchard Halliwell-Phillipps (1820-89)",
        },
        { key: "persnames-389", name: "Thomas Wright (1810-77)" },
      ],
      date_of_creation: [1859],
      place_of_origin: [],
      date_of_acquisition: [1859],
      related_material: "",
      related_sources: {
        individuals: [],
        works: [],
        texts: ["Reading"],
        sources: [],
        performances: [],
      },
      related_people: {
        acquirers: [
          "Queen Victoria (1819-1901), Queen of Great Britain and Ireland",
        ],
        donors: [],
        publishers: [],
      },
      media: [
        {
          label: "1",
          iiif_manifest_url: "/rct/iiif/732115a/",
          iiif_image_url: "/rct/iiif/image/34658",
          full_image_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/max/0/default.jpg",
          thumbnail_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
          image_width: 4015,
          image_height: 2980,
          thumbnail_width: 175,
          thumbnail_height: 130,
        },
      ],
      search_content:
        " A Glossary or collection of words, phrases, names and allusions to customs, proverbs etc ... in the works of English Authors particularly Shakespeare and his contemporaries ; vol. 1 1058899 Book ['Works', 'Text', 'Reading'] None",
      doc_type: "object",
    },
    {
      pk: 961,
      reference: "1058900",
      unittitle:
        "A Glossary or collection of words, phrases, names and allusions to customs, proverbs etc ... in the works of English Authors particularly Shakespeare and his contemporaries ; vol. 2",
      category: "Book",
      size: "1 item; 24.0 x 4.0 cm",
      medium: "book",
      label: "None",
      creators: [
        { key: "persnames-387", name: "Robert Nares (1753-1829)" },
        {
          key: "persnames-388",
          name: "James Orchard Halliwell-Phillipps (1820-89)",
        },
        { key: "persnames-389", name: "Thomas Wright (1810-77)" },
      ],
      date_of_creation: [1859],
      place_of_origin: [],
      date_of_acquisition: [1859],
      related_material: "",
      related_sources: {
        individuals: [],
        works: [],
        texts: ["Reading"],
        sources: [],
        performances: [],
      },
      related_people: {
        acquirers: [
          "Queen Victoria (1819-1901), Queen of Great Britain and Ireland",
        ],
        donors: [],
        publishers: [],
      },
      media: [
        {
          label: "1",
          iiif_manifest_url: "/rct/iiif/732115a/",
          iiif_image_url: "/rct/iiif/image/34658",
          full_image_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/max/0/default.jpg",
          thumbnail_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
          image_width: 4015,
          image_height: 2980,
          thumbnail_width: 175,
          thumbnail_height: 130,
        },
      ],
      search_content:
        " A Glossary or collection of words, phrases, names and allusions to customs, proverbs etc ... in the works of English Authors particularly Shakespeare and his contemporaries ; vol. 2 1058900 Book ['Works', 'Text', 'Reading'] None",
      doc_type: "object",
    },
    {
      pk: 1059,
      reference: "1059046",
      unittitle: "A Life of William Shakespeare",
      category: "Book",
      size: "1 item; 20.5 x 4.0 cm",
      medium: "book",
      label: "None",
      creators: [{ key: "persnames-432", name: "Sir Sidney Lee (1866-1949)" }],
      date_of_creation: [1898],
      place_of_origin: [],
      date_of_acquisition: [1898],
      related_material: "",
      related_sources: {
        individuals: ["Biographies"],
        works: [],
        texts: [],
        sources: [],
        performances: [],
      },
      related_people: { acquirers: [], donors: [], publishers: [] },
      media: [
        {
          label: "1",
          iiif_manifest_url: "/rct/iiif/732115a/",
          iiif_image_url: "/rct/iiif/image/34658",
          full_image_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/max/0/default.jpg",
          thumbnail_url:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
          image_width: 4015,
          image_height: 2980,
          thumbnail_width: 175,
          thumbnail_height: 130,
        },
      ],
      search_content:
        " A Life of William Shakespeare 1059046 Book ['None'] None",
      doc_type: "object",
    },
  ],
};

const events = {
  events: [
    {
      start_date: { year: 1648, display_date: 1648 },
      display_date: "1648",
      text: {
        headline:
          "Comedies, histories and tragedies,\npublished according\nto the true originall copies",
        text: "In the lead-up to his execution, while imprisoned at Windsor Castle, Charles I annotates his copy of Shakespeare's Second Folio. ",
      },
      unique_id: "1080415",
    },
    {
      start_date: { year: 1735, display_date: 1735 },
      display_date: "1735",
      text: {
        headline: "The Henry the Fifth Club, or The Gang",
        text: "In the midst of a longstanding dispute with his father, Frederick, Prince of Wales commissions a group portrait showing himself as Shakespeare's 'Prince Hal'",
      },
      unique_id: "405737",
    },
    {
      start_date: { year: 1737, display_date: 1737 },
      display_date: "1737",
      text: {
        headline: "Her Majesty's Library in St James's Park",
        text: "Queen Caroline has the library at St James's Palace remodelled and includes a bust of Shakespeare in the cornicing. ",
      },
      unique_id: "703051",
    },
    {
      start_date: { year: 1740, display_date: 1740 },
      display_date: "1740",
      text: {
        headline: "Shakespeare's Monument, Westminster Abbey",
        text: "William Kent issues his design for Shakespeare's new monument at Westminster Abbey, which is installed the following year. ",
      },
      unique_id: "66142",
    },
    {
      start_date: { year: 1746, display_date: 1746 },
      display_date: "1746",
      text: {
        headline: "David Garrick as Richard III",
        text: "Hogarth's print of David Garrick commemorates his meteoric rise to fame as a major Shakespearean actor, following his performance as Richard III in 1741. ",
      },
      unique_id: "654947",
    },
    {
      start_date: { year: 1765, display_date: 1765 },
      display_date: "1765",
      text: {
        headline: "Timon of Athens",
        text: "George III commissions a Shakespearean scene (in Classical dress) from the popular painter Nathaniel Dance Holland. ",
      },
      unique_id: "406725",
    },
    {
      start_date: { year: 1769, display_date: 1769 },
      display_date: "1769",
      text: {
        headline:
          "David Garrick Reciting the Ode in Honour of Shakespeare at the Jubilee in Stratfod",
        text: "David Garrick masterminds a multi-day 'Shakespeare Jubilee' at the dramatist's birthplace, Stratford-upon-Avon. A popular talking point, it helps spearhead the modern 'Shakespeare Industry. ",
      },
      unique_id: "655033",
    },
    {
      start_date: { year: 1781, display_date: 1781 },
      display_date: "1781",
      text: {
        headline: "Mrs Mary Robinson ('Perdita')",
        text: "George, Prince of Wales, commissions a portrait of the actress Mary Robinson as 'Perdita', following a brief affair between them during which he signed himself 'Florizel', with reference to the characters from The Winter's Tale. ",
      },
      unique_id: "400670",
    },
    {
      start_date: { year: 1800, display_date: 1800 },
      display_date: "1800",
      text: {
        headline:
          "Comedies, histories and tragedies,\npublished according\nto the true originall copies",
        text: "Charles I's copy of the Second Folio is bought back for the Royal Collection by George III. ",
      },
      unique_id: "1080415",
    },
    {
      start_date: { year: 1802, display_date: 1802 },
      display_date: "1802",
      text: {
        headline:
          "A Collection of Prints from pictures painted for the purpose of illustrating the Dramatic Works of Shakspeare",
        text: "Publication of the prints based on John Boydell's 'Shakespeare Gallery', a project designed to inspire and improve British art with reference to Shakespeare",
      },
      unique_id: "817106",
    },
    {
      start_date: { year: 1810, display_date: 1810 },
      display_date: "1810",
      text: {
        headline:
          "A Catalogue of Historical Prints Illustrative of Shakespear Plays. Published by John & Josiah Boydell 1802 Made by me at Frogmore.1810 Charlotte ",
        text: "While George III suffers his second serious bout of illness, Queen Charlotte draws up a catalogue of her collection of Shakespeare-themed prints published by John Boydell. ",
      },
      unique_id: "1047627",
    },
    {
      start_date: { year: 1816, display_date: 1816 },
      display_date: "1816",
      text: {
        headline: "A mulberry wood toothpick box",
        text: "In the bicentenary year of Shakespeare's death, the increasingly unpopular Prince Regent commissions a set of toothpick boxes made out of the wood of 'Shakespeare's mulberry tree' as gifts for friends and allies. ",
      },
      unique_id: "43894",
    },
    {
      start_date: { year: 1818, display_date: 1818 },
      display_date: "1818",
      text: {
        headline: "Mrs Siddons in the Trial Scene of Queen Katharine ",
        text: "George Henry Harlow's painting of Sarah Siddons as Shakespeare's Queen Katharine Is engraved, reflecting its enormous popularity. The image becomes a stock-in-trade for royal satirists for the next fifty years. ",
      },
      unique_id: "813150",
    },
    {
      start_date: { year: 1838, display_date: 1838 },
      display_date: "1838",
      text: {
        headline: "John Philip Kemble as Hamlet",
        text: "An engraving of Sir Thomas Lawrence's painting of John Philip Kemble as Hamlet is published, the year after William IV presented the original painting to the National Gallery. ",
      },
      unique_id: "657437",
    },
    {
      start_date: { year: 1840, display_date: 1840 },
      display_date: "1840",
      text: {
        headline: "Romeo and Tybalt",
        text: "The young Prince Albert and Queen Victoria study etching together, and work on scenes from Romeo and Juliet. ",
      },
      unique_id: "816031",
    },
    {
      start_date: { year: 1847, display_date: 1847 },
      display_date: "1847",
      text: {
        headline: "William Shakespeare",
        text: "Shakespeare's Birthplace is 'saved' for the nation, with the support of Prince Albert, who also purchases a mezzotint of the so-called 'Ashbourne Portrait' in its support. ",
      },
      unique_id: "661433",
    },
    {
      start_date: { year: 1848, display_date: 1848 },
      display_date: "1848",
      text: {
        headline: "The Disarming of Cupid",
        text: "Queen Victoria commissions William Edward Frost to paint a picture based on Shakespeare's Sonnet 154, as a pendant to paintings showing scenes from Edmund Spenser and John Milton. ",
      },
      unique_id: "407163",
    },
    {
      start_date: { year: 1850, display_date: 1850 },
      display_date: "1850",
      text: {
        headline: "Lesson books",
        text: "The future Edward VII copies out extracts from As You Like It, Macbeth and Julius Caesar in his lesson books. ",
      },
      unique_id: "VIC/ADDA05/470B",
    },
    {
      start_date: { year: 1853, display_date: 1853 },
      display_date: "1853",
      text: {
        headline: "The performance of Macbeth in the Rubens Room",
        text: "Between 1848-61, Charles Kean is invited to give a series of performances at Windsor Castle, including several Shakespeare plays. ",
      },
      unique_id: "919794",
    },
    {
      start_date: { year: 1857, display_date: 1857 },
      display_date: "1857",
      text: {
        headline: "The Entry of Bolingbroke ",
        text: "Princess Victoria presents her mother, Queen Victoria, with a watercolour showing a scene from Charles Kean's production of Richard II. ",
      },
      unique_id: "451134",
    },
    {
      start_date: { year: 1860, display_date: 1860 },
      display_date: "1860",
      text: {
        headline:
          "Windsor Castle, Royal Library, Queen Elizabeth Gallery (Room III), design for wooden cresting at doorway",
        text: "The Royal Library at Windsor is redesigned in the Elizabethan style by John Thomas, including a bust of Shakespeare in the doorway. ",
      },
      unique_id: "740072",
    },
    {
      start_date: { year: 1863, display_date: 1863 },
      display_date: "1863",
      text: {
        headline: "Bust of Shakespeare",
        text: "A tree identified as 'Herne's Oak' falls down in Windsor Great Park, and Queen Victoria commissions a series of relics from its remains. ",
      },
      unique_id: "7021",
    },
    {
      start_date: { year: 1888, display_date: 1888 },
      display_date: "1888",
      text: {
        headline:
          "Prince Arthur and Princess Margaret of Connaught as the Princes in the Tower",
        text: "The royal family put on a series of 'tableaux vivants' showing Shakespeare scenes (among others) for the birthday of Prince Henry of Battenburg ",
      },
      unique_id: "2980009",
    },
    {
      start_date: { year: 1893, display_date: 1893 },
      display_date: "1893",
      text: {
        headline: "The Works of William Shakespeare ('The Irving Shakespeare')",
        text: "Henry Irving presents his 'Irving Shakespeare' to George, Duke of York, and Princess May of Teck on the occasion of their wedding. ",
      },
      unique_id: "1056053",
    },
    {
      start_date: { year: 1917, display_date: 1917 },
      display_date: "1917",
      text: {
        headline: "The Merry Wives of Windsor, illustrated by Hugh Thomson",
        text: "Katharine Denison, a vicar's sister, embroiders a copy of The Merry Wives of Windsor and presents it to Queen Mary, mere months before the family change their name from Saxe-Coburg-Gotha to 'Windsor'",
      },
      unique_id: "1059106",
    },
    {
      start_date: { year: 1924, display_date: 1924 },
      display_date: "1924",
      text: {
        headline: "Oak Model of Shakespeare's Chair and Chest",
        text: "An amateur carver presents a model of Shakespeare's chair and chest to Queen Mary for her 'Dolls' House' project, initiated by Princess Marie-Louise of Schleswig-Holstein as a historical artefact and a spur to British trade and industry.",
      },
      unique_id: "55549",
    },
    {
      start_date: { year: 1944, display_date: 1944 },
      display_date: "1944",
      text: {
        headline: "Diary entry for 16 December 1944",
        text: "Henry V is screened in the Waterloo Chamber, Windsor",
      },
      unique_id: "GVI/PRIV/DIARY/WAR/1944: 16 DEC",
    },
    {
      start_date: { year: 1965, display_date: 1965 },
      display_date: "1965",
      text: {
        headline: "Charles, Prince of Wales as Macbeth",
        text: "Charles, Prince of Wales, performs as Macbeth in a school production at Gordonstoun.",
      },
      unique_id: "2813890",
    },
    {
      start_date: { year: 1970, display_date: 1970 },
      display_date: "1970",
      text: {
        headline: "Bank of England: Twenty Pounds",
        text: "The first £20 note to carry a portrait of the monarch is published, with an image of Shakespeare's monument in Westminster Abbey on the reverse. ",
      },
      unique_id: "445827",
    },
    {
      start_date: { year: 1991, display_date: 1991 },
      display_date: "1991",
      text: {
        headline: "Flower Vase",
        text: "On the occasion of her state visit to the USA, Elizabeth II is presented with a Shakespeare-inspired 'flower vase' by President George H. W. Bush",
      },
      unique_id: "95751",
    },
    {
      start_date: { year: 1997, display_date: 1997 },
      display_date: "1997",
      text: {
        headline: "Pewter bowl with designs inspired by Shakespeare's Globe",
        text: "Queen Elizabeth II is presented with a commemorative bowl at the formal opening of the new Globe Theatre on the South Bank. ",
      },
      unique_id: "94637",
    },
  ],
};
const themes = {
  themes: [
    {
      id: 1,
      title: "William Shakespeare",
      featuredObjects: [
        {
          reference: "40497",
          category: "Decorative arts",
          title: "Box with a view of Stratford church",
          id: 1380,
          creators: [
            "Henrik Immanuel Wigström (1862-1923)",
            "Carl Fabergé (1846-1920)",
          ],
          creation_date: 1903,
          resource:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
        },
        {
          reference: "406072",
          category: "Painting",
          title: "Portrait of a Man",
          id: 1383,
          creators: ["None"],
          creation_date: 1620,
          resource:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
        },
        {
          reference: "447173.a",
          category: "Medals",
          title: "Commemorative medal",
          id: 1404,
          creators: ["Milan Knobloch (b.1921)"],
          creation_date: 2004,
          resource:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
        },
        {
          reference: "661421",
          category: "Print",
          title: "William Shakespeare",
          id: 1862,
          creators: [
            "Martin Droeshout (1601-after 1639)",
            "Ben Jonson (c.1637-c.1572)",
          ],
          creation_date: 1685,
          resource:
            "https://rct.resourcespace.com/iiif/image/39758/full/thm/0/default.jpg",
        },
      ],
    },
    {
      id: 1,
      title: "On the Page",
      featuredObjects: [
        {
          reference: "1059072",
          category: "Book",
          title:
            "A Most pleasant and excellent conceited Comedy of Sir John Falstaffe, and the merry VVives of VVindsor. VVith the swaggering vaine of Ancient Pistoll, and Corporall Nym",
          id: 1077,
          creators: ["William Shakespeare (1564-1616)"],
          creation_date: 1619,
          resource:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
        },
        {
          reference: "813725",
          category: "None",
          title: "The Quarrel of Oberon and Titania",
          id: 2097,
          creators: ["Sir Joseph Noël Paton (1821-1901)"],
          creation_date: 1847,
          resource:
            "https://rct.resourcespace.com/iiif/image/39962/full/thm/0/default.jpg",
        },
      ],
    },
    {
      id: 1,
      title: "On the Stage",
      featuredObjects: [
        {
          reference: "2913567",
          category: "Photograph",
          title: "Miss C Leclercq as Ariel",
          id: 1343,
          creators: ["Camille Silvy (1834-1910)"],
          creation_date: 1856,
          resource:
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg",
        },
        {
          reference: "655013",
          category: "Print",
          title: "Mr Garrick and Mrs Pritchard as Macbeth and Lady Macbeth",
          id: 1631,
          creators: [
            "Johann Joseph Zoffany (1733-1810)",
            "Valentine Green (1739-1813)",
          ],
          creation_date: 1776,
          resource:
            "https://rct.resourcespace.com/iiif/image/39707/full/thm/0/default.jpg",
        },
        {
          reference: "913000",
          category: "Painting",
          title: "A Scene from Macbeth, Act I",
          id: 2122,
          creators: ["Louis Haghe (1806-85)"],
          creation_date: 1853,
          resource:
            "https://rct.resourcespace.com/iiif/image/52819/full/thm/0/default.jpg",
        },
      ],
    },
  ],
};
const STATIC_WAGTAIL_OBJECTS = {
  meta: {
    total_count: 1,
  },
  items: [
    {
      id: 8,
      meta: {
        type: "editor.SharcRichTextPage",
        detail_url: "http://localhost/api/wagtail/pages/8/",
        html_url: "http://localhost/sharc-home/objects/",
        slug: "objects",
        show_in_menus: false,
        first_published_at: "2021-01-21T11:27:32.474733Z",
      },
      title: "Objects",
      body: "<p>An object description</p>",
    },
  ],
};
const STATIC_MENU_ITEMS = {
  items: [
    {
      id: 3,
      meta: {
        type: "editor.SharcRichTextPage",
        detail_url: "http://localhost/api/wagtail/pages/3/",
        html_url: "http://localhost/sharc-home/",
        slug: "sharc-home",
        show_in_menus: true,
        seo_title: "",
        search_description: "",
        first_published_at: "2021-05-14T11:09:29.266613Z",
        parent: {
          id: 2,
          meta: {
            type: "wagtailcore.Page",
            detail_url: "http://localhost/api/wagtail/pages/2/",
            html_url: "http://localhost/",
          },
          title: "Welcome to your new Wagtail site!",
        },
      },
      title: "Sharc home",
      body: "<p>This is a test description for the home page</p>",
      body_html: "<p>This is a test description for the home page</p>",
      menu_children: [
        {
          id: 9,
          title: "Objects",
          slug: "objects",
          menu_children: [],
        },
        {
          id: 4,
          title: "Events",
          slug: "events",
          menu_children: [],
        },
        {
          id: 6,
          title: "About",
          slug: "about",
          menu_children: [],
        },
        {
          id: 8,
          title: "Themes",
          slug: "themes",
          menu_children: [
            {
              id: 16,
              title: "On the stage",
              slug: "on-the-stage",
              menu_children: [],
            },
            {
              id: 17,
              title: "William Shakespeare",
              slug: "william-shakespeare",
              menu_children: [],
            },
          ],
        },
      ],
    },
  ],
};
const STATIC_WAGTAIL_EVENTS = {
  meta: {
    total_count: 1,
  },
  items: [
    {
      id: 14,
      meta: {
        type: "editor.StreamFieldPage",
        detail_url: "http://localhost/api/wagtail/pages/14/",
        html_url: "http://localhost/sharc-home/events/",
        slug: "events",
        show_in_menus: true,
        first_published_at: "2021-02-22T17:12:14.759406Z",
      },
      title: "Events",
      body: [
        {
          type: "heading",
          value: "A test Heading",
          id: "ee1ff036-94c0-4426-ad85-56ac44c8e311",
        },
        {
          type: "paragraph",
          value:
            '<p>Some text, and <b>some others.</b> A <a href="https://kdl.kcl.ac.uk">link</a> in a paragraph</p>',
          id: "4cdf3829-5873-4b42-bf6c-cee0e652c5da",
        },
        {
          type: "two_column_section",
          value: [
            {
              heading: "Event 1",
              body: "<p>Some stuff</p>",
            },
            {
              heading: "Event 2",
              body: "<p>Some other stuff</p>",
            },
          ],
          id: "67c2980e-85a8-461f-9427-7c1958eee52b",
        },
        {
          type: "image",
          value: {
            id: 1,
            filename: "Charles_Is_Shakespeare.jpg",
            full_url:
              "https://sharc.kcl.ac.uk/static/Charles%20I's%20Shakespeare.jpg",
            full_width: 1000,
            full_height: 764,
          },
          id: "2aca4dae-42c7-46e5-a899-1c89bdd2e756",
        },
        {
          type: "embed",
          value: {
            html: '<div>\n    <iframe width="200" height="113" src="https://www.youtube.com/embed/xk4aNAZ557w?feature=oembed" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>\n</div>\n',
            url: "https://www.youtube.com/watch?v=xk4aNAZ557w",
          },
          id: "620587b7-dd12-4728-8866-06030e94b1e6",
        },
        {
          type: "document",
          value: {
            title: "Digital Twins",
            filename: "Digital_twin_report.pdf",
            url: "/documents/1/Digital_twin_report.pdf",
          },
          id: "aa949028-6608-4a95-b557-9d55dae9726c",
        },
        {
          type: "page",
          value: 4,
          id: "ed17de42-d805-4d61-a299-5439701cd055",
        },
      ],
    },
  ],
};
const STATIC_WAGTAIL_HOME = {
  meta: {
    total_count: 1,
  },
  items: [
    {
      id: 3,
      meta: {
        type: "editor.SharcRichTextPage",
        detail_url: "http://localhost/api/wagtail/pages/3/",
        html_url: "http://localhost/sharc-home/",
        slug: "sharc-home",
        show_in_menus: false,
        first_published_at: "2021-01-07T12:16:18.867309Z",
      },
      title: "Home",
      body: "<p>home</p>",
    },
  ],
};

const STATIC_WAGTAIL_ABOUT = {
  meta: {
    total_count: 1,
  },
  items: [
    {
      id: 6,
      meta: {
        type: "editor.StreamFieldPage",
        detail_url: "http://localhost/api/wagtail/pages/6/",
        html_url: "http://localhost/sharc-home/about/",
        slug: "about",
        first_published_at: "2021-01-21T11:24:46.321022Z",
      },
      title: "About",
      body: [
        {
          type: "heading",
          value: "About",
          id: "fc40e462-3fa1-4de6-a343-0000c5d3ade4",
        },
        {
          type: "paragraph",
          value:
            "<p>What has Shakespeare done for the royal family, and what has the royal family done for Shakespeare? This is the central research question of ‘Shakespeare in the Royal Collection’, a three-year AHRC funded project (launched in September 2018), which focuses on the Shakespeare-related holdings in the Royal Collection and the stories they have to tell, primarily during the period 1714-1945.</p><p>Shakespeare and the royal family have long had a close, interdependent relationship. Shakespeare addresses royal history in many of his plays; his works have also functioned across the centuries as a vehicle for the development of royal ideology and for the education of young royals. Equally, royal patronage has tangibly affected the nature of the Shakespearean afterlife. Each has, in key ways, legitimised the other.</p><p>A key dimension of this history has been the inclusion of Shakespeare-related items – manuscripts, paintings, prints, drawings, performance records, printed books, photographs, and other objects – in the Royal Collection. These objects, never systematically researched, will be the primary subject of investigation over the course of this project, which will produce:</p><ul><li>a publicly accessible database of all the Shakespeare-related holdings, and set of 3D visualisations of key spaces at Windsor Castle where Shakespeare’s plays were performed.</li><li>Two monographs, written by the postdoctoral research associates</li><li>A collection of essays focusing on a series of individual objects in the Collections</li><li>An exhibition of selected Shakespeare-related holdings</li><li>A major TV documentary</li></ul>",
          id: "5408b121-2e6e-464f-b62a-aa394d79e4d6",
        },
        {
          type: "heading",
          value: "Funders",
          id: "aa6d31c4-6600-44af-a52b-d40e092a07cd",
        },
        {
          type: "paragraph",
          value:
            '<p>Funded by the <a href="http://ahrc.ukri.org/">Arts and Humanities Research Council</a>, in partnership with the Royal Collection Trust.</p>',
          id: "6a40d654-a325-42cb-97a1-8cabffd3c4e3",
        },
        {
          type: "image",
          value: {
            id: 20,
            filename: "Charles_Is_Shakespeare.jpg",
            full_url:
              "https://sharc.kcl.ac.uk/static/Charles%20I's%20Shakespeare.jpg",
            full_width: 1000,
            full_height: 764,
          },
          id: "3616f4b5-3f24-4354-b67e-85a2d260a98d",
        },
        {
          type: "gallery",
          value: {
            show_in_menus: true,
            images_block: [
              {
                show_in_menus: true,
                transcription: "",
                description: "",
                attribution: "",
                caption:
                  "William Shakespeare, Comedies, histories and tragedies (Charles I’s copy of Shakespeare’s complete works), 1632, folio bound in red goatskin (RCIN 1080415)",
                page: null,
                url: "",
                alignment: "float-left",
                image: 3,
              },
              {
                show_in_menus: true,
                transcription: "",
                description: "",
                attribution: "",
                caption:
                  "Leonida Caldesi, Prince Arthur and Prince Leopold in the costume of the sons of King Henry IV, albumen print hand-coloured with watercolour, 1859 (RCIN 2914286)",
                page: null,
                url: "",
                alignment: "float-left",
                image: 2,
              },
              {
                show_in_menus: true,
                transcription: "",
                description: "",
                attribution: "",
                caption:
                  "William Perry, A Treatise on the Identity of Herne’s Oak, book bound in the wood of Herne’s Oak, 1867 (RCIN 1047000)",
                page: null,
                url: "",
                alignment: "float-left",
                image: 6,
              },
            ],
          },
          id: "a251a790-d52c-483a-a069-a3a3e4566765",
        },
        {
          type: "image",
          value: {
            id: 2,
            filename: "TheEntryOfBolingbroke.jpg",
            full_url:
              "https://sharc.kcl.ac.uk/static/Entry%20of%20Bolingbroke.jpg",
            full_width: 441,
            full_height: 500,
          },
          id: "b0662fb5-06ec-42a5-9fae-8397eed7ebd8",
        },
        {
          type: "image",
          value: {
            id: 19,
            filename: "George_IV_as_Florizel.jpg",
            full_url:
              "http://sharc.kcl.ac.uk/static/George%20IV%20as%20Florizel.jpg",
            full_width: 1000,
            full_height: 789,
          },
          id: "97f0f85e-94bf-486f-a580-7e1ad1c0a186",
        },
        {
          type: "image",
          value: {
            id: 18,
            filename: "Mulberry_boxes.jpg",
            full_url: "https://sharc.kcl.ac.uk/static/Mulberry%20boxes.jpg",
            full_width: 1000,
            full_height: 526,
          },
          id: "f73995e3-e03a-4d02-b290-e60aaffccbb3",
        },
        {
          type: "image",
          value: {
            id: 17,
            filename: "Treatise_on_Hernes_Oak.jpg",
            full_url:
              "https://sharc.kcl.ac.uk/static/Treatise%20on%20Herne's%20Oak.jpg",
            full_width: 1000,
            full_height: 1330,
          },
          id: "2b1286d6-7374-4540-bd41-32fea3a88738",
        },
        {
          type: "image",
          value: {
            id: 16,
            filename: "Arthur_and_Leopold.jpg",
            full_url:
              "https://sharc.kcl.ac.uk/static/Arthur%20and%20Leopold.jpg",
            full_width: 1000,
            full_height: 1265,
          },
          id: "5431e0bc-b829-4f3b-89fd-ad6e3d37f677",
        },
        {
          type: "heading",
          value: "Project Team",
          id: "01f5bc2b-51b2-4d0e-88ce-f6cff2d529cf",
        },
        {
          type: "paragraph",
          value:
            '<div class="two-column-50-50">\n' +
            "<div>\n" +
            "<h3>Gordon McMullan</h3>\n" +
            "<h4>(Principal Investigator)</h4>\n" +
            "<p>Gordon is Professor of English at King’s College London and Director of the London Shakespeare Centre. His publications include <i>The Politics of Unease in the Plays of John Fletcher</i> (1994), the Arden Shakespeare edition of <i>Henry VIII</i> (2000), <i>Shakespeare and the Idea of Late Writing</i> (2007), <i>Antipodal Shakespeare</i> (2018) and several edited and co-edited collections, including <i>Late Style and its Discontents</i> (2017). He is a general textual editor of <i>The Norton Shakespeare, 3rd edition</i> (2016), for which he also edited <i>Romeo and Juliet</i>.</p>\n" +
            "</div>\n" +
            "<div>\n" +
            "<h3>Kate Retford</h3>\n" +
            "<h4>(Co-Investigator)</h4>\n" +
            "<p>Kate is Professor of the History of Art at Birkbeck, University of London. Her publications include <i>The Art of Domestic Life: Family Portraiture in Eighteenth-Century England</i> (2006), a co-authored monograph <i>Advancing with the Army</i> (2006) and <i>The Conversation Piece: Making Modern Art in Eighteenth-Century Britain</i> (2017); she has also co-edited two collections, <i>Placing Faces: The Portrait and the English Country House in the Long Eighteenth Century</i> (2013; with Gill Perry et al) and <i>The Georgian London Town House</i> (2019; with Susanna Avery-Quash).</p>\n" +
            "</div>\n" +
            "<div>\n" +
            "<h3>Sally Barnden</h3><h4>(Postdoctoral Research Associate)</h4><p>Sally has a PhD in Shakespeare studies from King’s College London. She did scoping work for the grant by way of an internal postdoctoral research associateship in 2016-17. Her monograph, <i>Still Shakespeare and the Photography of Performance</i>, was published in 2020 by Cambridge University Press.</p>\n" +
            "</div>\n" +
            "<div>\n" +
            "<h3>Kirsten Tambling</h3>\n" +
            "<h4>(Postdoctoral Research Associate)</h4>\n" +
            "<p>Kirsten has a PhD from Birkbeck entitled ‘Making the Crossing: Seduction, Space and Time in the Art of William Hogarth and Jean-Antoine Watteau’. She previously studied at Cambridge (English and Eighteenth-Century Studies) and the Courtauld (Curating the Art Museum) and held a Curatorial Internship at the Royal Collection in 2014-15.</p>\n" +
            "</div>\n" +
            "</div>",

          id: "301a325b-e36f-4224-9f66-9e8dcb6f87a0",
        },
        {
          type: "heading",
          value: "Contact us",
          id: "747de18e-290e-4eda-a6a5-857839ba7d6f",
        },
        {
          type: "paragraph",
          value:
            '<p>For all enquiries, contact us at sharc@kcl.ac.uk</p><p>For ongoing updates on the project follow us on <a href="http://twitter.com/sharc_project">Twitter</a></p>',
          id: "8cd3d537-00fd-4d83-a0a6-cecbd07ac0b5",
        },
      ],
    },
  ],
};
const STATIC_WAGTAIL_ACCESSIBILITY = {};
const STATIC_WAGTAIL_RESOURCES = {
  meta: {
    total_count: 1,
  },
  items: [
    {
      id: 5,
      meta: {
        type: "editor.StreamFieldPage",
        detail_url: "http://localhost/api/wagtail/pages/5/",
        html_url: "http://localhost/sharc-home/resources/",
        slug: "resources",
        first_published_at: "2021-01-21T11:18:20.322758Z",
      },
      title: "Resources",
      body: [
        {
          type: "heading",
          value: "A resource test pages",
          id: "59b584b8-ccf0-45ef-a5bc-1db8441b7e6d",
        },
        {
          type: "paragraph",
          value: "<p>Some text</p>",
          id: "3f1f99c2-d35a-4baa-9642-f79ad719c641",
        },
        {
          type: "document",
          value: {
            title: "Digital Twin report",
            filename: "Digital_twin_report.pdf",
            url: "/documents/1/Digital_twin_report.pdf",
          },
          id: "775fa226-2bd0-4b5d-94ba-c98f74aad502",
        },
      ],
    },
  ],
};
const STATIC_WAGTAIL_GLOSSARY = {};
const STATIC_WAGTAIL_BIBLIOGRAPHY = {};
const STATIC_WAGTAIL_ACKNOWLEDGEMENTS = {};

const wagtail_static_data = {
  "sharc-home": STATIC_WAGTAIL_HOME,
  about: STATIC_WAGTAIL_ABOUT,
  objects: STATIC_WAGTAIL_OBJECTS,
  accessibility: STATIC_WAGTAIL_ACCESSIBILITY,
  events: STATIC_WAGTAIL_EVENTS,
  resources: STATIC_WAGTAIL_RESOURCES,
  glossary: STATIC_WAGTAIL_GLOSSARY,
  bibliography: STATIC_WAGTAIL_BIBLIOGRAPHY,
  acknowledgements: STATIC_WAGTAIL_ACKNOWLEDGEMENTS,
  menu_items: STATIC_MENU_ITEMS,
};

async function getUrl(url) {
  return axios.get(url, {
    headers: getHeaders(),
  });
}

async function get(action, params) {
  if (process.env.VUE_APP_API_URL === "STATIC") {
    if (action === "documents/") {
      return { data: documents };
    } else if (action === "events/") {
      return { data: events };
    } else if (action === "themes/") {
      return { data: themes };
    }
    //const response = {"data":page_8};
    //return response;
  } else {
    return axios.get(`${API_URL}/${action}`, {
      headers: getHeaders(),
      params: getParams(params),
    });
  }
}

async function getWagtailRichTextPage(action, slug) {
  if (process.env.VUE_APP_API_URL === "STATIC") {
    return { data: wagtail_static_data[slug] };
  } else {
      console.log(slug);
    return axios.get(`${API_URL}/${action}`, {
      headers: getHeaders(),
      params: getWagtailParams({
        slug: slug,
        type: "editor.SharcRichTextPage",
        fields: "title,body,show_in_menus",
      }),
    });
  }
}

async function getWagtailMenuPages(action) {
  if (process.env.VUE_APP_API_URL === "STATIC") {
    return { data: wagtail_static_data["menu_items"] };
  } else {
    return getWagtailPage(
      action,
      process.env.VUE_APP_WAGTAIL_HOME_SLUG,
      "editor.SharcRichTextPage",
      "menu_children"
    );
  }
}

async function getWagtailPage(action, slug, type, fields) {
  if (process.env.VUE_APP_API_URL === "STATIC") {
    return { data: wagtail_static_data[slug] };
  } else {
      console.log('slug:' + slug);
    return axios.get(`${API_URL}/${action}`, {
      headers: getHeaders(),
      params: getWagtailParams({ slug: slug, type: type, fields: fields }),
    });
  }
}

async function getSingle(action, id) {
  // strip the trailing slash if it's there
  const url = API_URL.replace(/\/$/, "");
  return axios.get(`${url}${action}${id}`, {
    headers: getHeaders(),
  });
}

function getHeaders() {
  return {
    Bearer: `Token ${TOKEN}`,
  };
}

/**
 * Get and transform params for an api request
 * @param params
 */
/*
        params include page number, selected filters and selected sorting option
        {
            searchTerm: '',
            pages: 1,
            selectedFacets: [
                {category: "shakespeare_connection", display_name: "Individual"},
                {category: "shakespeare_connection", display_name: "Works"},
                {category: "play", display_name: "Henry V"},
                {category: "play", display_name: "Richard III"},
                {category: "relation_to_objects", display_name: "Portrait"},
                {category: "relation_to_objects", display_name: "Performance"}
            ],
            sort: {
                desc: false,
                sort_by: "name"
            }
        }

        NB: If needed, I can also change the structure of the selectedFacets to, for example, {category: "play", selected_options: ["Henry V", "Richard III"]}.

        */
/**
 * Convenience method for adding necessary wagtail params for api
 * @param params
 */
function getWagtailParams(params) {
  // todo add param elements as they get working in the api
  let searchParams = new URLSearchParams();
  if (params) {
    //Wagtail page by Slug filter
    if (params.slug) {
      searchParams.append("slug", params.slug);
    }
    if (params.type) {
      // Page type
      searchParams.append("type", params.type);
    }
    if (params.fields) {
      // Page fields to retrieve
      searchParams.append("fields", params.fields);
    }
  }
  return searchParams;
}

function getParams(params) {
  let searchParams = new URLSearchParams();

  if (params) {
    if (params.searchTerm) {
      searchParams.append("search_multi_match", params.searchTerm);
    }
    if (params.pages) {
      searchParams.append("pages", params.pages);
    }
    if (params.sort && params.sort.sort_by.length > 0) {
      // todo finish
      //sort: {sort_by: "name", desc: true}
      let sort = "";
      if (params.sort.desc === true) {
        sort = "-";
      }
      searchParams.append("ordering", sort + params.sort.sort_by);
    }
    // Extended parsing for years
    if (params.creation_years) {
      if (params.creation_years[0] > 0) {
        searchParams.append(
          "date_of_creation__range",
          params.creation_years[0] + "__" + params.creation_years[1]
        );
      }
    }
    if (params.acquisition_years) {
      if (params.acquisition_years[0] > 0) {
        searchParams.append(
          "date_of_acquisition__range",
          params.acquisition_years[0] + "__" + params.acquisition_years[1]
        );
      }
    }
    // Facets, currently AND searching for all
    if (params.selectedFacets && params.selectedFacets.length > 0) {
      for (var facet in params.selectedFacets) {
        if (params.selectedFacets[facet].category.includes("__")) {
          // term already has extra controls e.g. __lte
          searchParams.append(
            params.selectedFacets[facet].category,
            params.selectedFacets[facet].key
          );
        } else {
          searchParams.append(
            params.selectedFacets[facet].category + "__term",
            params.selectedFacets[facet].key
          );
        }
      }
    }
  }

  return searchParams;
}

const Api = {
  getUrl,
  get,
  getSingle,
  getParams,
  getWagtailRichTextPage,
  getWagtailPage,
  getWagtailMenuPages,
  stripUrl,
};
export default Api;
