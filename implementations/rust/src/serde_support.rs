//! Serde integration for CFG++ values

#[cfg(feature = "serde")]
use serde::{Deserialize, Deserializer, Serialize, Serializer};
use crate::value::CfgppValue;
use std::collections::HashMap;

#[cfg(feature = "serde")]
impl Serialize for CfgppValue {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        match self {
            CfgppValue::Null => serializer.serialize_none(),
            CfgppValue::Boolean(b) => serializer.serialize_bool(*b),
            CfgppValue::Integer(i) => serializer.serialize_i64(*i),
            CfgppValue::Double(d) => serializer.serialize_f64(*d),
            CfgppValue::String(s) | CfgppValue::Enum(s) => serializer.serialize_str(s),
            CfgppValue::Array(arr) => arr.serialize(serializer),
            CfgppValue::Object(obj) => obj.serialize(serializer),
        }
    }
}

#[cfg(feature = "serde")]
impl<'de> Deserialize<'de> for CfgppValue {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        use serde::de::{self, MapAccess, SeqAccess, Visitor};
        use std::fmt;

        struct ValueVisitor;

        impl<'de> Visitor<'de> for ValueVisitor {
            type Value = CfgppValue;

            fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
                formatter.write_str("a valid CFG++ value")
            }

            fn visit_bool<E>(self, value: bool) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(CfgppValue::Boolean(value))
            }

            fn visit_i8<E>(self, value: i8) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(CfgppValue::Integer(value as i64))
            }

            fn visit_i16<E>(self, value: i16) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(CfgppValue::Integer(value as i64))
            }

            fn visit_i32<E>(self, value: i32) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(CfgppValue::Integer(value as i64))
            }

            fn visit_i64<E>(self, value: i64) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(CfgppValue::Integer(value))
            }

            fn visit_u8<E>(self, value: u8) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(CfgppValue::Integer(value as i64))
            }

            fn visit_u16<E>(self, value: u16) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(CfgppValue::Integer(value as i64))
            }

            fn visit_u32<E>(self, value: u32) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(CfgppValue::Integer(value as i64))
            }

            fn visit_u64<E>(self, value: u64) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                if value <= i64::MAX as u64 {
                    Ok(CfgppValue::Integer(value as i64))
                } else {
                    Ok(CfgppValue::Double(value as f64))
                }
            }

            fn visit_f32<E>(self, value: f32) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(CfgppValue::Double(value as f64))
            }

            fn visit_f64<E>(self, value: f64) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(CfgppValue::Double(value))
            }

            fn visit_str<E>(self, value: &str) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(CfgppValue::String(value.to_string()))
            }

            fn visit_string<E>(self, value: String) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(CfgppValue::String(value))
            }

            fn visit_none<E>(self) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(CfgppValue::Null)
            }

            fn visit_some<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
            where
                D: Deserializer<'de>,
            {
                CfgppValue::deserialize(deserializer)
            }

            fn visit_unit<E>(self) -> Result<Self::Value, E>
            where
                E: de::Error,
            {
                Ok(CfgppValue::Null)
            }

            fn visit_seq<A>(self, mut seq: A) -> Result<Self::Value, A::Error>
            where
                A: SeqAccess<'de>,
            {
                let mut vec = Vec::new();

                while let Some(element) = seq.next_element()? {
                    vec.push(element);
                }

                Ok(CfgppValue::Array(vec))
            }

            fn visit_map<A>(self, mut map: A) -> Result<Self::Value, A::Error>
            where
                A: MapAccess<'de>,
            {
                let mut object = HashMap::new();

                while let Some((key, value)) = map.next_entry()? {
                    object.insert(key, value);
                }

                Ok(CfgppValue::Object(object))
            }
        }

        deserializer.deserialize_any(ValueVisitor)
    }
}

/// Convert CFG++ value to JSON string
#[cfg(feature = "serde")]
pub fn to_json(value: &CfgppValue) -> crate::error::CfgppResult<String> {
    serde_json::to_string_pretty(value)
        .map_err(|e| crate::error::CfgppError::parse_error(e.to_string()))
}

/// Convert CFG++ value to compact JSON string
#[cfg(feature = "serde")]
pub fn to_json_compact(value: &CfgppValue) -> crate::error::CfgppResult<String> {
    serde_json::to_string(value)
        .map_err(|e| crate::error::CfgppError::parse_error(e.to_string()))
}

/// Parse CFG++ value from JSON string
#[cfg(feature = "serde")]
pub fn from_json(json: &str) -> crate::error::CfgppResult<CfgppValue> {
    serde_json::from_str(json)
        .map_err(|e| crate::error::CfgppError::parse_error(e.to_string()))
}

/// Convert CFG++ value to TOML string
#[cfg(all(feature = "serde", feature = "toml"))]
pub fn to_toml(value: &CfgppValue) -> crate::error::CfgppResult<String> {
    toml::to_string_pretty(value)
        .map_err(|e| crate::error::CfgppError::parse_error(e.to_string()))
}

/// Parse CFG++ value from TOML string
#[cfg(all(feature = "serde", feature = "toml"))]
pub fn from_toml(toml: &str) -> crate::error::CfgppResult<CfgppValue> {
    toml::from_str(toml)
        .map_err(|e| crate::error::CfgppError::parse_error(e.to_string()))
}

/// Convert CFG++ value to YAML string
#[cfg(all(feature = "serde", feature = "yaml"))]
pub fn to_yaml(value: &CfgppValue) -> crate::error::CfgppResult<String> {
    serde_yaml::to_string(value)
        .map_err(|e| crate::error::CfgppError::parse_error(e.to_string()))
}

/// Parse CFG++ value from YAML string
#[cfg(all(feature = "serde", feature = "yaml"))]
pub fn from_yaml(yaml: &str) -> crate::error::CfgppResult<CfgppValue> {
    serde_yaml::from_str(yaml)
        .map_err(|e| crate::error::CfgppError::parse_error(e.to_string()))
}

#[cfg(test)]
#[cfg(feature = "serde")]
mod tests {
    use super::*;
    use std::collections::HashMap;

    #[test]
    fn test_json_roundtrip() {
        let mut obj = HashMap::new();
        obj.insert("name".to_string(), CfgppValue::string("test"));
        obj.insert("value".to_string(), CfgppValue::integer(42));
        obj.insert("enabled".to_string(), CfgppValue::boolean(true));
        
        let original = CfgppValue::object_with_values(obj);
        
        let json = to_json(&original).unwrap();
        let parsed = from_json(&json).unwrap();
        
        assert_eq!(original, parsed);
    }

    #[test]
    fn test_array_serialization() {
        let array = CfgppValue::array_with_values(vec![
            CfgppValue::integer(1),
            CfgppValue::integer(2),
            CfgppValue::integer(3),
        ]);
        
        let json = to_json(&array).unwrap();
        assert!(json.contains("["));
        assert!(json.contains("1"));
        assert!(json.contains("2"));
        assert!(json.contains("3"));
    }

    #[test]
    fn test_null_serialization() {
        let null_value = CfgppValue::null();
        let json = to_json(&null_value).unwrap();
        assert_eq!(json.trim(), "null");
    }
}
