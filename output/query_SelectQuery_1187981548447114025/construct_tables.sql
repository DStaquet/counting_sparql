CREATE TABLE IF NOT EXISTS BGP_4185401599073693870 (product VARCHAR(255),
                                                            value1 VARCHAR(255),
                                                                   label VARCHAR(255),
                                                                         k_count INT, PRIMARY KEY (product,
                                                                                                   value1,
                                                                                                   label));


DROP TABLE IF EXISTS delta_BGP_4185401599073693870;


CREATE TABLE IF NOT EXISTS delta_BGP_4185401599073693870 (product VARCHAR(255),
                                                                  value1 VARCHAR(255),
                                                                         label VARCHAR(255),
                                                                               k_count INT, PRIMARY KEY (product,
                                                                                                         value1,
                                                                                                         label));


CREATE TABLE IF NOT EXISTS nu_BGP_4185401599073693870 (product VARCHAR(255),
                                                               value1 VARCHAR(255),
                                                                      label VARCHAR(255),
                                                                            k_count INT, PRIMARY KEY (product,
                                                                                                      value1,
                                                                                                      label));


CREATE TABLE IF NOT EXISTS Filter_2470482819316668795 (label VARCHAR(255),
                                                             product VARCHAR(255),
                                                                     value1 VARCHAR(255),
                                                                            k_count INT, PRIMARY KEY (product,
                                                                                                      value1,
                                                                                                      label));


DROP TABLE IF EXISTS delta_Filter_2470482819316668795;


CREATE TABLE IF NOT EXISTS delta_Filter_2470482819316668795 (label VARCHAR(255),
                                                                   product VARCHAR(255),
                                                                           value1 VARCHAR(255),
                                                                                  k_count INT, PRIMARY KEY (product,
                                                                                                            value1,
                                                                                                            label));


CREATE TABLE IF NOT EXISTS nu_Filter_2470482819316668795 (label VARCHAR(255),
                                                                product VARCHAR(255),
                                                                        value1 VARCHAR(255),
                                                                               k_count INT, PRIMARY KEY (product,
                                                                                                         value1,
                                                                                                         label));


CREATE TABLE IF NOT EXISTS Project_6725609393674109187 (label VARCHAR(255),
                                                              product VARCHAR(255),
                                                                      k_count INT, PRIMARY KEY (product,
                                                                                                label));


DROP TABLE IF EXISTS delta_Project_6725609393674109187;


CREATE TABLE IF NOT EXISTS delta_Project_6725609393674109187 (label VARCHAR(255),
                                                                    product VARCHAR(255),
                                                                            k_count INT, PRIMARY KEY (product,
                                                                                                      label));


CREATE TABLE IF NOT EXISTS nu_Project_6725609393674109187 (label VARCHAR(255),
                                                                 product VARCHAR(255),
                                                                         k_count INT, PRIMARY KEY (product,
                                                                                                   label));


CREATE TABLE IF NOT EXISTS SelectQuery_1187981548447114025 (label VARCHAR(255),
                                                                  product VARCHAR(255),
                                                                          k_count INT, PRIMARY KEY (product,
                                                                                                    label));


DROP TABLE IF EXISTS delta_SelectQuery_1187981548447114025;


CREATE TABLE IF NOT EXISTS delta_SelectQuery_1187981548447114025 (label VARCHAR(255),
                                                                        product VARCHAR(255),
                                                                                k_count INT, PRIMARY KEY (product,
                                                                                                          label));


CREATE TABLE IF NOT EXISTS nu_SelectQuery_1187981548447114025 (label VARCHAR(255),
                                                                     product VARCHAR(255),
                                                                             k_count INT, PRIMARY KEY (product,
                                                                                                       label));